namespace VersionSelector;

partial class MainForm
{
    private System.ComponentModel.IContainer components = null!;
    private ListView lstVersions = null!;
    private ColumnHeader colName = null!;
    private ColumnHeader colStatus = null!;
    private ColumnHeader colPort = null!;
    private Button btnStart = null!;
    private Button btnStop = null!;
    private Button btnRestart = null!;
    private Button btnRefresh = null!;
    private Label lblMessage = null!;
    private System.Windows.Forms.Timer refreshTimer = null!;

    protected override void Dispose(bool disposing)
    {
        if (disposing && components is not null)
        {
            components.Dispose();
        }
        base.Dispose(disposing);
    }

    private void InitializeComponent()
    {
        components = new System.ComponentModel.Container();

        lstVersions = new ListView();
        colName = new ColumnHeader { Text = "Version", Width = 220 };
        colStatus = new ColumnHeader { Text = "Status", Width = 120 };
        colPort = new ColumnHeader { Text = "Port", Width = 80 };
        btnStart = new Button();
        btnStop = new Button();
        btnRestart = new Button();
        btnRefresh = new Button();
        lblMessage = new Label();
        refreshTimer = new System.Windows.Forms.Timer(components);

        SuspendLayout();

        // lstVersions
        // WinForms' UI Automation provider exposes Control.Name as
        // AutomationId (not AccessibleName -- that maps to the UIA "Name"
        // property instead), so AutomationIds.* constants go on .Name here
        // for FlaUI's ByAutomationId() to actually find these controls.
        lstVersions.Name = AutomationIds.VersionsListView;
        lstVersions.AccessibleName = "Versions";
        lstVersions.View = View.Details;
        lstVersions.FullRowSelect = true;
        lstVersions.MultiSelect = false;
        lstVersions.HideSelection = false;
        lstVersions.Location = new Point(12, 12);
        lstVersions.Size = new Size(440, 200);
        lstVersions.Columns.AddRange(new[] { colName, colStatus, colPort });
        lstVersions.SelectedIndexChanged += (_, _) => UpdateButtonStates();

        // btnStart
        btnStart.Name = AutomationIds.StartButton;
        btnStart.AccessibleName = "Start";
        btnStart.Text = "Start";
        btnStart.Location = new Point(12, 224);
        btnStart.Size = new Size(100, 30);
        btnStart.Click += (_, _) => OnActionClicked(DockerAction.Up);

        // btnStop
        btnStop.Name = AutomationIds.StopButton;
        btnStop.AccessibleName = "Stop";
        btnStop.Text = "Stop";
        btnStop.Location = new Point(120, 224);
        btnStop.Size = new Size(100, 30);
        btnStop.Click += (_, _) => OnActionClicked(DockerAction.Down);

        // btnRestart
        btnRestart.Name = AutomationIds.RestartButton;
        btnRestart.AccessibleName = "Restart";
        btnRestart.Text = "Restart";
        btnRestart.Location = new Point(228, 224);
        btnRestart.Size = new Size(100, 30);
        btnRestart.Click += (_, _) => OnActionClicked(DockerAction.Restart);

        // btnRefresh
        btnRefresh.Name = AutomationIds.RefreshButton;
        btnRefresh.AccessibleName = "Refresh";
        btnRefresh.Text = "Refresh";
        btnRefresh.Location = new Point(352, 224);
        btnRefresh.Size = new Size(100, 30);
        btnRefresh.Click += (_, _) => RefreshStatuses();

        // lblMessage
        lblMessage.Name = AutomationIds.MessageLabel;
        lblMessage.AccessibleName = "Message";
        lblMessage.Location = new Point(12, 264);
        lblMessage.Size = new Size(440, 60);
        lblMessage.Text = "";

        // refreshTimer
        refreshTimer.Interval = 5000;
        refreshTimer.Tick += (_, _) => RefreshStatuses();

        // MainForm
        AutoScaleDimensions = new SizeF(7F, 15F);
        AutoScaleMode = AutoScaleMode.Font;
        ClientSize = new Size(464, 340);
        Controls.Add(lstVersions);
        Controls.Add(btnStart);
        Controls.Add(btnStop);
        Controls.Add(btnRestart);
        Controls.Add(btnRefresh);
        Controls.Add(lblMessage);
        Name = "MainForm";
        Text = "Hospital Directory API - Version Selector";

        ResumeLayout(false);
    }
}
