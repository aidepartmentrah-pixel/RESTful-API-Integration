using VersionSelector;
using Xunit;

namespace VersionSelector.Tests;

public class DockerComposeCommandBuilderTests
{
    [Fact]
    public void BuildArguments_Up_UsesDetachedFlag()
    {
        var args = DockerComposeCommandBuilder.BuildArguments("mock-v11", DockerAction.Up);
        Assert.Equal("compose -p mock-v11 up -d", args);
    }

    [Fact]
    public void BuildArguments_Down()
    {
        var args = DockerComposeCommandBuilder.BuildArguments("mock-v11", DockerAction.Down);
        Assert.Equal("compose -p mock-v11 down", args);
    }

    [Fact]
    public void BuildArguments_Restart()
    {
        var args = DockerComposeCommandBuilder.BuildArguments("mock-v12-dev", DockerAction.Restart);
        Assert.Equal("compose -p mock-v12-dev restart", args);
    }

    [Fact]
    public void BuildPsArguments_FiltersByComposeProjectLabel()
    {
        var args = DockerComposeCommandBuilder.BuildPsArguments("mock-v11");
        Assert.Contains("label=com.docker.compose.project=mock-v11", args);
    }
}
