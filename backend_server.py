# backend_server.py - Central Controller for OmniCore Operator Loop
import asyncio
import json
import websockets

# Import modular engines
from engine_voice import VoiceEngine
from engine_vision import VisionEngine
from engine_planner import PlannerEngine
import engine_automation as automation

# Global sessions
clients = set()
voice_eng = VoiceEngine()
vision_eng = VisionEngine()
planner_eng = PlannerEngine()

# Keep track of active task execution states
agent_state = {
    "pending_task": None,
    "pending_steps": None,
    "pending_intent": None,
    "safety_confirmation_needed": False
}

async def send_status(websocket, status: str, task: str = "", step: str = "", pct: int = 0):
    """Broadcast current execution status markers to client UI."""
    payload = {
        "type": "status_update",
        "status": status,  # "Thinking...", "Planning...", "Executing...", "Observing...", "Completed"
        "task": task,
        "step": step,
        "percentage": pct
    }
    await websocket.send(json.dumps(payload))

async def handle_safety_check(websocket, user_text: str) -> bool:
    """Check if action is blocked by Safety Shield and handle confirmation loops."""
    global agent_state
    
    # User is confirming a pending safety block
    if agent_state["safety_confirmation_needed"]:
        txt = user_text.lower().strip()
        if any(w in txt for w in ["yes", "confirm", "proceed", "haan", "ho", "sari", "avunu", "ha"]):
            # Proceed with the execution
            await websocket.send(json.dumps({
                "role": "assistant",
                "content": f"🛡️ Safety approved. Proceeding with execution..."
            }))
            agent_state["safety_confirmation_needed"] = False
            
            # Execute steps
            steps = agent_state["pending_steps"]
            intent = agent_state["pending_intent"]
            await execute_operator_loop(websocket, steps, intent)
            return True
        else:
            # Cancel task
            await websocket.send(json.dumps({
                "role": "assistant",
                "content": f"❌ Action cancelled by user."
            }))
            agent_state["safety_confirmation_needed"] = False
            agent_state["pending_task"] = None
            agent_state["pending_steps"] = None
            agent_state["pending_intent"] = None
            return True

    # Check incoming goal text for safety concerns
    safety_alert = planner_eng.check_safety(user_text)
    if safety_alert:
        steps, intent = planner_eng.plan_steps(user_text)
        agent_state["pending_task"] = user_text
        agent_state["pending_steps"] = steps
        agent_state["pending_intent"] = intent
        agent_state["safety_confirmation_needed"] = True
        
        # Ask user for approval
        await websocket.send(json.dumps({
            "role": "assistant",
            "content": safety_alert
        }))
        voice_eng.speak(safety_alert)
        return True
        
    return False

async def execute_operator_loop(websocket, steps: list, intent: dict):
    """Run core autonomous loop: Execute -> Observe Screen -> Verify -> Complete."""
    total_steps = len(steps)
    exec_results = []
    
    # ─── Loop: Action Execution ───────────────────────────────────────────────
    for idx, step in enumerate(steps):
        current_step_name = step.get("step", "Executing action")
        pct = int(((idx + 1) / total_steps) * 80) # reserve 20% for observation/completion
        
        # Update UI: Executing
        await send_status(websocket, "Executing...", intent["display"], current_step_name, pct)
        
        # Run automation step safely in thread pool to prevent loop blocking
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, automation.execute_steps, [step])
        exec_results.extend(res)
        
        # ─── Loop: Screen Observation & Decision Making ─────────────────────────
        await send_status(websocket, "Observing...", intent["display"], f"Verifying {current_step_name}", pct + 5)
        obs = await loop.run_in_executor(None, vision_eng.observe_screen)
        
        # Verify result (Self-Correction/Retry engine)
        # If execution result contains a failed indicator, retry once
        if any("failed" in str(r).lower() for r in res):
            await websocket.send(json.dumps({
                "role": "assistant",
                "content": f"⚠️ Detection alert: Action failed. Retrying step: {current_step_name}..."
            }))
            # Retry
            res_retry = await loop.run_in_executor(None, automation.execute_steps, [step])
            exec_results.extend(res_retry)

    # ─── Loop: Completed ──────────────────────────────────────────────────────
    await send_status(websocket, "Completed", intent["display"], "All tasks verified", 100)
    
    localized_done = planner_eng.get_localized_string("done")
    localized_plan_prefix = planner_eng.get_localized_string("plan_prefix")
    
    # Build complete detailed reply
    plan_checklist = "\n".join([f"{i+1}. {s['step']}" for i, s in enumerate(steps)])
    final_reply = f"{localized_done}\n\n**{localized_plan_prefix}**\n{plan_checklist}"
    
    await websocket.send(json.dumps({
        "role": "assistant",
        "content": final_reply
    }))
    
    # Local Text-to-Speech speech synthesis output
    voice_eng.speak(localized_done)

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"WS Incoming: {message}")
            try:
                data = json.loads(message)
                user_text = data.get('content', '').strip()
                if not user_text:
                    continue
                
                # Check for safety blocks first
                is_handled = await handle_safety_check(websocket, user_text)
                if is_handled:
                    continue
                
                # NLU Language & Planning Update
                await send_status(websocket, "Thinking...", user_text, "Parsing goal", 5)
                await asyncio.sleep(0.3)
                
                await send_status(websocket, "Planning...", user_text, "Generating steps plan", 15)
                steps, intent = planner_eng.plan_steps(user_text)
                
                # Run the automated executor loop
                await execute_operator_loop(websocket, steps, intent)

            except Exception as e:
                import traceback
                traceback.print_exc()
                await websocket.send(json.dumps({
                    "role": "assistant",
                    "content": f"⚠️ Operator Error: {str(e)}"
                }))
    finally:
        clients.discard(websocket)

if __name__ == "__main__":
    async def main():
        async with websockets.serve(handler, "localhost", 8767):
            print("OmniCore AI Operator running on ws://localhost:8767")
            await asyncio.Future()
    asyncio.run(main())
