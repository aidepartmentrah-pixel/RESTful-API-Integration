using VersionSelector;
using Xunit;

namespace VersionSelector.Tests;

public class FakeDockerRunnerTests
{
    [Fact]
    public void RunCompose_RecordsInvocation()
    {
        var runner = new FakeDockerRunner();

        runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Up);

        var invoked = Assert.Single(runner.InvokedCommands);
        Assert.Equal(@"C:\fake\repo", invoked.WorkingDirectory);
        Assert.Equal("mock-v11", invoked.ComposeProject);
        Assert.Equal(DockerAction.Up, invoked.Action);
    }

    [Fact]
    public void RunCompose_Up_TransitionsStatusToRunning()
    {
        var runner = new FakeDockerRunner();
        runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Up);
        Assert.Equal(DockerPsStatus.Running, runner.GetStatus("mock-v11"));
    }

    [Fact]
    public void RunCompose_Down_TransitionsStatusToStopped()
    {
        var runner = new FakeDockerRunner();
        runner.StatusByProject["mock-v11"] = DockerPsStatus.Running;

        runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Down);

        Assert.Equal(DockerPsStatus.Stopped, runner.GetStatus("mock-v11"));
    }

    [Fact]
    public void RunCompose_WhenSimulatingUnavailable_ReturnsUnavailableResult()
    {
        var runner = new FakeDockerRunner { SimulateUnavailable = true };

        var result = runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Up);

        Assert.True(result.DockerUnavailable);
        Assert.False(result.Success);
    }

    [Fact]
    public void GetStatus_UnknownProject_DefaultsToStopped()
    {
        var runner = new FakeDockerRunner();
        Assert.Equal(DockerPsStatus.Stopped, runner.GetStatus("never-seen"));
    }

    [Fact]
    public void LoadFromStateFile_ReadsStatusesAndUnavailableFlag()
    {
        var statePath = Path.GetTempFileName();
        try
        {
            File.WriteAllText(statePath, """
                { "unavailable": false, "statuses": { "mock-v11": "Running", "mock-v12-dev": "Stopped" } }
                """);

            var runner = FakeDockerRunner.LoadFromStateFile(statePath, logFilePath: null);

            Assert.Equal(DockerPsStatus.Running, runner.GetStatus("mock-v11"));
            Assert.Equal(DockerPsStatus.Stopped, runner.GetStatus("mock-v12-dev"));
        }
        finally
        {
            File.Delete(statePath);
        }
    }

    [Fact]
    public void RunCompose_WithLogFilePath_AppendsOneJsonLinePerCall()
    {
        var logPath = Path.GetTempFileName();
        try
        {
            var runner = new FakeDockerRunner(logPath);
            runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Up);
            runner.RunCompose(@"C:\fake\repo", "mock-v11", DockerAction.Down);

            var lines = File.ReadAllLines(logPath);
            Assert.Equal(2, lines.Length);
            Assert.Contains("mock-v11", lines[0]);
            Assert.Contains("Up", lines[0]);
            Assert.Contains("Down", lines[1]);
        }
        finally
        {
            File.Delete(logPath);
        }
    }
}
