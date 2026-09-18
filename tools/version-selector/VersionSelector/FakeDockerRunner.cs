using System.Text.Json;

namespace VersionSelector;

public sealed record InvokedCommand(string WorkingDirectory, string ComposeProject, DockerAction Action);

/// <summary>
/// In-memory stand-in for IDockerRunner, used two ways:
///   1. Constructed directly by fast unit tests (DockerComposeCommandBuilderTests
///      etc. don't need this, but FakeDockerRunnerTests does) to assert on
///      InvokedCommands without touching real Docker.
///   2. Constructed by Program.cs when VERSION_SELECTOR_FAKE_DOCKER_STATE is
///      set, so the *compiled EXE itself* runs against a fake Docker when
///      launched by the fast FlaUI suite -- real UI automation, no real
///      Docker dependency. Each RunCompose call is appended to a log file an
///      external test process can read back after driving the UI.
/// </summary>
public sealed class FakeDockerRunner : IDockerRunner
{
    public List<InvokedCommand> InvokedCommands { get; } = new();
    public Dictionary<string, DockerPsStatus> StatusByProject { get; } = new();
    public bool SimulateUnavailable { get; set; }

    private readonly string? _logFilePath;

    public FakeDockerRunner(string? logFilePath = null)
    {
        _logFilePath = logFilePath;
    }

    public DockerCommandResult RunCompose(string workingDirectory, string composeProject, DockerAction action)
    {
        var record = new InvokedCommand(workingDirectory, composeProject, action);
        InvokedCommands.Add(record);
        AppendLog(record);

        if (SimulateUnavailable)
        {
            return new DockerCommandResult { Success = false, DockerUnavailable = true };
        }

        StatusByProject[composeProject] = action switch
        {
            DockerAction.Up => DockerPsStatus.Running,
            DockerAction.Down => DockerPsStatus.Stopped,
            DockerAction.Restart => DockerPsStatus.Running,
            _ => StatusByProject.GetValueOrDefault(composeProject, DockerPsStatus.Unknown),
        };

        return new DockerCommandResult { Success = true, DockerUnavailable = false };
    }

    public DockerPsStatus GetStatus(string composeProject)
    {
        if (SimulateUnavailable)
        {
            return DockerPsStatus.Unavailable;
        }
        return StatusByProject.GetValueOrDefault(composeProject, DockerPsStatus.Stopped);
    }

    private void AppendLog(InvokedCommand record)
    {
        if (_logFilePath is null)
        {
            return;
        }
        var line = JsonSerializer.Serialize(new
        {
            record.WorkingDirectory,
            record.ComposeProject,
            Action = record.Action.ToString(),
        });
        File.AppendAllText(_logFilePath, line + Environment.NewLine);
    }

    /// <summary>Reads the state fixture used by Program.cs's test mode. Shape:
    /// { "unavailable": false, "statuses": { "projectName": "Running" } }</summary>
    public static FakeDockerRunner LoadFromStateFile(string stateFilePath, string? logFilePath)
    {
        var json = File.ReadAllText(stateFilePath);
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        var runner = new FakeDockerRunner(logFilePath);

        if (root.TryGetProperty("unavailable", out var unavailableEl))
        {
            runner.SimulateUnavailable = unavailableEl.GetBoolean();
        }

        if (root.TryGetProperty("statuses", out var statusesEl))
        {
            foreach (var prop in statusesEl.EnumerateObject())
            {
                if (Enum.TryParse<DockerPsStatus>(prop.Value.GetString(), ignoreCase: true, out var status))
                {
                    runner.StatusByProject[prop.Name] = status;
                }
            }
        }

        return runner;
    }
}
