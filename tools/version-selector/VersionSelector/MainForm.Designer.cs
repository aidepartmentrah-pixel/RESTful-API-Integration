#nullable enable
using System.Drawing.Drawing2D;

namespace VersionSelector;

partial class MainForm
{
    private System.ComponentModel.IContainer components = null!;
    private Panel headerPanel = null!;
    private Panel logoPanel = null!;
    private Label lblTitle = null!;
    private Label lblSubtitle = null!;
    private Panel statusCard = null!;
    private Label lblRegistryCaption = null!;
    private Label lblRegistryValue = null!;
    private Label lblVersionsCaption = null!;
    private Label lblVersionsValue = null!;
    private ListView lstVersions = null!;
    private ColumnHeader colName = null!;
    private ColumnHeader colStatus = null!;
    private ColumnHeader colPort = null!;
    private Button btnStart = null!;
    private Button btnStop = null!;
    private Button btnRestart = null!;
    private Button btnRefresh = null!;
    private Panel footerPanel = null!;
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

        headerPanel = new Panel();
        logoPanel = new Panel();
        lblTitle = new Label();
        lblSubtitle = new Label();
        statusCard = new Panel();
        lblRegistryCaption = new Label();
        lblRegistryValue = new Label();
        lblVersionsCaption = new Label();
        lblVersionsValue = new Label();
        lstVersions = new ListView();
        colName = new ColumnHeader { Text = "Version", Width = 220 };
        colStatus = new ColumnHeader { Text = "Status", Width = 130 };
        colPort = new ColumnHeader { Text = "Port", Width = 90 };
        btnStart = new Button();
        btnStop = new Button();
        btnRestart = new Button();
        btnRefresh = new Button();
        footerPanel = new Panel();
        lblMessage = new Label();
        refreshTimer = new System.Windows.Forms.Timer(components);

        SuspendLayout();

        // headerPanel -- accent-colored band, same look as rah-backup-widget's
        // header Border (Styles.xaml AccentBrush / MainWindow.xaml header).
        headerPanel.Dock = DockStyle.Top;
        headerPanel.Height = 72;
        headerPanel.BackColor = Theme.Accent;

        // logoPanel -- translucent rounded box + "API" text, matching the
        // reference app's in-window logo (Border Background="#33FFFFFF").
        logoPanel.Location = new Point(20, 16);
        logoPanel.Size = new Size(40, 40);
        logoPanel.BackColor = Color.Transparent;
        logoPanel.Paint += LogoPanel_Paint;

        lblTitle.Text = "Hospital Directory API";
        lblTitle.ForeColor = Color.White;
        lblTitle.Font = new Font("Segoe UI", 13F, FontStyle.Bold);
        lblTitle.Location = new Point(72, 12);
        lblTitle.Size = new Size(440, 26);
        lblTitle.BackColor = Color.Transparent;

        lblSubtitle.Text = "Local version selector";
        lblSubtitle.ForeColor = Color.FromArgb(0xEB, 0xD9, 0xD1);
        lblSubtitle.Font = new Font("Segoe UI", 9F);
        lblSubtitle.Location = new Point(72, 40);
        lblSubtitle.Size = new Size(440, 20);
        lblSubtitle.BackColor = Color.Transparent;

        headerPanel.Controls.Add(logoPanel);
        headerPanel.Controls.Add(lblTitle);
        headerPanel.Controls.Add(lblSubtitle);

        // statusCard -- white card with a thin themed border, same idea as
        // rah-backup-widget's CardBorder style / status summary card.
        statusCard.Location = new Point(20, 92);
        statusCard.Size = new Size(600, 76);
        statusCard.BackColor = Theme.Card;
        statusCard.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        statusCard.Paint += CardBorder_Paint;

        lblRegistryCaption.Text = "Registry file:";
        lblRegistryCaption.ForeColor = Theme.SecondaryText;
        lblRegistryCaption.Location = new Point(16, 14);
        lblRegistryCaption.Size = new Size(160, 20);

        lblRegistryValue.Text = "";
        lblRegistryValue.ForeColor = Theme.PrimaryText;
        lblRegistryValue.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
        lblRegistryValue.Location = new Point(180, 14);
        lblRegistryValue.Size = new Size(404, 20);
        lblRegistryValue.AutoEllipsis = true;
        lblRegistryValue.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;

        lblVersionsCaption.Text = "Versions tracked:";
        lblVersionsCaption.ForeColor = Theme.SecondaryText;
        lblVersionsCaption.Location = new Point(16, 42);
        lblVersionsCaption.Size = new Size(160, 20);

        lblVersionsValue.Text = "0";
        lblVersionsValue.ForeColor = Theme.PrimaryText;
        lblVersionsValue.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
        lblVersionsValue.Location = new Point(180, 42);
        lblVersionsValue.Size = new Size(404, 20);

        statusCard.Controls.Add(lblRegistryCaption);
        statusCard.Controls.Add(lblRegistryValue);
        statusCard.Controls.Add(lblVersionsCaption);
        statusCard.Controls.Add(lblVersionsValue);

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
        lstVersions.GridLines = true;
        lstVersions.BackColor = Theme.Card;
        lstVersions.BorderStyle = BorderStyle.FixedSingle;
        lstVersions.Location = new Point(20, 230);
        lstVersions.Size = new Size(600, 210);
        lstVersions.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
        lstVersions.Columns.AddRange(new[] { colName, colStatus, colPort });
        lstVersions.SelectedIndexChanged += (_, _) => UpdateButtonStates();

        // btnStart -- the one primary/filled action, same convention as
        // rah-backup-widget's Tag="Primary" button style.
        btnStart.Name = AutomationIds.StartButton;
        btnStart.AccessibleName = "Start";
        btnStart.Text = "Start";
        btnStart.Location = new Point(20, 184);
        btnStart.Size = new Size(110, 34);
        btnStart.FlatStyle = FlatStyle.Flat;
        btnStart.FlatAppearance.BorderColor = Theme.AccentDark;
        btnStart.FlatAppearance.MouseOverBackColor = Theme.AccentDark;
        btnStart.BackColor = Theme.Accent;
        btnStart.ForeColor = Color.White;
        btnStart.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
        btnStart.Cursor = Cursors.Hand;
        btnStart.Click += (_, _) => OnActionClicked(DockerAction.Up);

        // btnStop / btnRestart / btnRefresh -- neutral outlined buttons.
        ConfigureSecondaryButton(btnStop, AutomationIds.StopButton, "Stop", new Point(140, 184));
        btnStop.Click += (_, _) => OnActionClicked(DockerAction.Down);

        ConfigureSecondaryButton(btnRestart, AutomationIds.RestartButton, "Restart", new Point(250, 184));
        btnRestart.Click += (_, _) => OnActionClicked(DockerAction.Restart);

        ConfigureSecondaryButton(btnRefresh, AutomationIds.RefreshButton, "Refresh", new Point(360, 184));
        btnRefresh.Click += (_, _) => RefreshStatuses();

        // footerPanel -- thin accent-tinted status strip, same idea as
        // rah-backup-widget's bottom StatusBar (AccentLight/AccentDark).
        footerPanel.Dock = DockStyle.Bottom;
        footerPanel.Height = 64;
        footerPanel.BackColor = Theme.AccentLight;

        lblMessage.Name = AutomationIds.MessageLabel;
        lblMessage.AccessibleName = "Message";
        lblMessage.ForeColor = Theme.AccentDark;
        lblMessage.Location = new Point(20, 8);
        lblMessage.Size = new Size(600, 48);
        lblMessage.Text = "";

        footerPanel.Controls.Add(lblMessage);

        // refreshTimer
        refreshTimer.Interval = 5000;
        refreshTimer.Tick += (_, _) => RefreshStatuses();

        // MainForm
        AutoScaleDimensions = new SizeF(7F, 15F);
        AutoScaleMode = AutoScaleMode.Font;
        BackColor = Theme.Background;
        ClientSize = new Size(640, 520);
        MinimumSize = new Size(680, 560);
        Controls.Add(lstVersions);
        Controls.Add(btnStart);
        Controls.Add(btnStop);
        Controls.Add(btnRestart);
        Controls.Add(btnRefresh);
        Controls.Add(statusCard);
        Controls.Add(footerPanel);
        Controls.Add(headerPanel);
        Name = "MainForm";
        Text = "Hospital Directory API - Version Selector";

        ResumeLayout(false);
    }

    private void ConfigureSecondaryButton(Button button, string automationId, string text, Point location)
    {
        button.Name = automationId;
        button.AccessibleName = text;
        button.Text = text;
        button.Location = location;
        button.Size = new Size(100, 34);
        button.FlatStyle = FlatStyle.Flat;
        button.BackColor = Theme.Card;
        button.ForeColor = Theme.PrimaryText;
        button.FlatAppearance.BorderColor = Theme.Border;
        button.FlatAppearance.MouseOverBackColor = Theme.AccentLight;
        button.Cursor = Cursors.Hand;
    }

    private void LogoPanel_Paint(object? sender, PaintEventArgs e)
    {
        e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
        var bounds = logoPanel.ClientRectangle;
        bounds.Width -= 1;
        bounds.Height -= 1;
        using var path = RoundedRectangle.Path(bounds, 8);
        using var fill = new SolidBrush(Color.FromArgb(51, 255, 255, 255));
        e.Graphics.FillPath(fill, path);

        using var font = new Font("Segoe UI", 9.5F, FontStyle.Bold);
        using var textBrush = new SolidBrush(Color.White);
        using var format = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
        e.Graphics.DrawString("API", font, textBrush, logoPanel.ClientRectangle, format);
    }

    private void CardBorder_Paint(object? sender, PaintEventArgs e)
    {
        var bounds = statusCard.ClientRectangle;
        bounds.Width -= 1;
        bounds.Height -= 1;
        using var pen = new Pen(Theme.Border);
        e.Graphics.DrawRectangle(pen, bounds);
    }
}
