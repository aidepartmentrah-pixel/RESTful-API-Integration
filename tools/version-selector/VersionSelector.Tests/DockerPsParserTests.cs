using VersionSelector;
using Xunit;

namespace VersionSelector.Tests;

public class DockerPsParserTests
{
    [Fact]
    public void Parse_EmptyOutput_IsStopped()
    {
        Assert.Equal(DockerPsStatus.Stopped, DockerPsParser.Parse(""));
    }

    [Fact]
    public void Parse_AllContainersRunning_IsRunning()
    {
        var output = "mock-v11-api-1\trunning\nmock-v11-postgres-1\trunning\nmock-v11-pgadmin-1\trunning\n";
        Assert.Equal(DockerPsStatus.Running, DockerPsParser.Parse(output));
    }

    [Fact]
    public void Parse_SomeContainersCreatedNotYetRunning_IsStarting()
    {
        var output = "mock-v11-api-1\tcreated\nmock-v11-postgres-1\trunning\n";
        Assert.Equal(DockerPsStatus.Starting, DockerPsParser.Parse(output));
    }

    [Fact]
    public void Parse_AllContainersExited_IsStopped()
    {
        var output = "mock-v11-api-1\texited\nmock-v11-postgres-1\texited\n";
        Assert.Equal(DockerPsStatus.Stopped, DockerPsParser.Parse(output));
    }

    [Fact]
    public void Parse_IsCaseInsensitive()
    {
        var output = "mock-v11-api-1\tRunning\n";
        Assert.Equal(DockerPsStatus.Running, DockerPsParser.Parse(output));
    }

    [Fact]
    public void Parse_IgnoresMalformedLines()
    {
        var output = "not-tab-separated\nmock-v11-api-1\trunning\n";
        Assert.Equal(DockerPsStatus.Running, DockerPsParser.Parse(output));
    }
}
