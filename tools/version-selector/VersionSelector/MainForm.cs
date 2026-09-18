namespace VersionSelector;

public partial class MainForm : Form
{
    private readonly IReadOnlyList<VersionEntry> _versions;
    private readonly IDockerRunner _dockerRunner;

    public MainForm(IReadOnlyList<VersionEntry> versions, IDockerRunner dockerRunner)
    {
        _versions = versions;
        _dockerRunner = dockerRunner;

        InitializeComponent();

        foreach (var version in _versions)
        {
            var item = new ListViewItem(new[] { version.Name, "Unknown", version.Port.ToString() });
            lstVersions.Items.Add(item);
        }

        if (lstVersions.Items.Count > 0)
        {
            lstVersions.Items[0].Selected = true;
        }

        UpdateButtonStates();
        Load += (_, _) =>
        {
            RefreshStatuses();
            refreshTimer.Start();
        };
    }

    private VersionEntry? SelectedVersion =>
        lstVersions.SelectedIndices.Count == 0 ? null : _versions[lstVersions.SelectedIndices[0]];

    private void UpdateButtonStates()
    {
        var hasSelection = SelectedVersion is not null;
        btnStart.Enabled = hasSelection;
        btnStop.Enabled = hasSelection;
        btnRestart.Enabled = hasSelection;
    }

    private void RefreshStatuses()
    {
        var anyUnavailable = false;

        for (var i = 0; i < _versions.Count; i++)
        {
            var status = _dockerRunner.GetStatus(_versions[i].ComposeProject);
            lstVersions.Items[i].SubItems[1].Text = status.ToString();
            if (status == DockerPsStatus.Unavailable)
            {
                anyUnavailable = true;
            }
        }

        if (anyUnavailable)
        {
            lblMessage.Text = "Docker does not appear to be available. Is Docker Desktop running?";
            lblMessage.ForeColor = Color.Firebrick;
        }
    }

    private void OnActionClicked(DockerAction action)
    {
        var version = SelectedVersion;
        if (version is null)
        {
            return;
        }

        btnStart.Enabled = false;
        btnStop.Enabled = false;
        btnRestart.Enabled = false;
        lblMessage.ForeColor = SystemColors.ControlText;
        lblMessage.Text = $"Running docker compose {ActionLabel(action)} for {version.Name}...";
        Refresh();

        var result = _dockerRunner.RunCompose(version.WorkingDirectory, version.ComposeProject, action);

        if (result.DockerUnavailable)
        {
            lblMessage.Text = "Docker does not appear to be available. Is Docker Desktop running?";
            lblMessage.ForeColor = Color.Firebrick;
        }
        else if (!result.Success)
        {
            lblMessage.Text = $"docker compose {ActionLabel(action)} failed for {version.Name}:\n{result.StandardError}";
            lblMessage.ForeColor = Color.Firebrick;
        }
        else
        {
            lblMessage.Text = $"{version.Name}: {ActionLabel(action)} succeeded.";
            lblMessage.ForeColor = Color.DarkGreen;
        }

        UpdateButtonStates();
        RefreshStatuses();
    }

    private static string ActionLabel(DockerAction action) => action switch
    {
        DockerAction.Up => "up",
        DockerAction.Down => "down",
        DockerAction.Restart => "restart",
        _ => action.ToString(),
    };
}
