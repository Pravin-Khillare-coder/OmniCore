using System;
using System.IO;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace OmniCoreWin
{
    public class MainForm : Form
    {
        private WebView2 webView;

        public MainForm()
        {
            InitializeComponent();
            Load += MainForm_Load;
        }

        private async void MainForm_Load(object? sender, EventArgs e)
        {
            // Ensure the WebView2 runtime is installed
            var env = await CoreWebView2Environment.CreateAsync();
            await webView.EnsureCoreWebView2Async(env);

            // Load the local index.html bundled with the app
            string exePath = AppDomain.CurrentDomain.BaseDirectory;
            string indexPath = Path.Combine(exePath, "index.html");
            if (File.Exists(indexPath))
            {
                webView.Source = new Uri(indexPath);
            }
            else
            {
                MessageBox.Show($"UI file not found: {indexPath}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void InitializeComponent()
        {
            this.webView = new WebView2();
            SuspendLayout();
            // 
            // webView
            // 
            this.webView.Dock = DockStyle.Fill;
            this.webView.CreationProperties = null;
            this.webView.Name = "webView";
            this.webView.Size = new System.Drawing.Size(800, 600);
            this.webView.TabIndex = 0;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(96F, 96F);
            this.AutoScaleMode = AutoScaleMode.Dpi;
            this.ClientSize = new System.Drawing.Size(800, 600);
            this.Controls.Add(this.webView);
            this.Name = "MainForm";
            this.Text = "OmniCore Assistant";
            this.StartPosition = FormStartPosition.CenterScreen;
            ResumeLayout(false);
        }
    }
}
