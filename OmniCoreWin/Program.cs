using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace OmniCoreWin
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            // Path to bundled backend executable (produced by PyInstaller)
            string backendPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "backend_server.exe");
            var startInfo = new ProcessStartInfo
            {
                FileName = backendPath,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };

            Process backendProcess = null;
            try
            {
                backendProcess = Process.Start(startInfo);
                if (backendProcess != null)
                {
                    backendProcess.OutputDataReceived += (s, e) => { if (e.Data != null) Console.WriteLine("[Backend] " + e.Data); };
                    backendProcess.ErrorDataReceived += (s, e) => { if (e.Data != null) Console.Error.WriteLine("[Backend ERR] " + e.Data); };
                    backendProcess.BeginOutputReadLine();
                    backendProcess.BeginErrorReadLine();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to start backend: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            Application.SetHighDpiMode(HighDpiMode.SystemAware);
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());

            // Ensure backend is terminated when UI closes
            try
            {
                if (backendProcess != null && !backendProcess.HasExited)
                {
                    backendProcess.Kill();
                }
            }
            catch { }
        }
    }
}
