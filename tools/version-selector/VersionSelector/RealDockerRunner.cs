using System.ComponentModel;
using System.Diagnostics;

namespace VersionSelector;

/// <summary>Shells out to the real `docker` executable.</summary>
public sealed class RealDockerRunner : IDockerRunner
{
    private const int TimeoutMs = 120_000;

    public DockerCommandResult RunCompose(string workingDirectory, string composeProject, DockerAction action)
    {
        var arguments = DockerComposeCommandBuilder.BuildArguments(composeProject, action);
        return Execute(workingDirectory, arguments);
    }

    public DockerPsStatus GetStatus(string composeProject)
    {
        var arguments = DockerComposeCommandBuilder.BuildPsArguments(composeProject);
        var result = Execute(Environment.CurrentDirectory, arguments);
        if (result.DockerUnavailable)
        {
            return DockerPsStatus.Unavailable;
        }
        if (!result.Success)
        {
            return DockerPsStatus.Unknown;
        }
        return DockerPsParser.Parse(result.StandardOutput);
    }

    private static DockerCommandResult Execute(string workingDirectory, string arguments)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = "docker",
            Arguments = arguments,
            WorkingDirectory = workingDirectory,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        try
        {
            using var process = Process.Start(startInfo);
            if (process is null)
            {
                return new DockerCommandResult { Success = false, DockerUnavailable = true };
            }

            var stdout = process.StandardOutput.ReadToEnd();
            var stderr = process.StandardError.ReadToEnd();
            var exited = process.WaitForExit(TimeoutMs);
            if (!exited)
            {
                try { process.Kill(entireProcessTree: true); } catch { /* best effort */ }
                return new DockerCommandResult
                {
                    Success = false,
                    DockerUnavailable = false,
                    StandardOutput = stdout,
                    StandardError = "Timed out waiting for docker to respond.",
                };
            }

            return new DockerCommandResult
            {
                Success = process.ExitCode == 0,
                DockerUnavailable = false,
                StandardOutput = stdout,
                StandardError = stderr,
            };
        }
        catch (Win32Exception)
        {
            // docker.exe not found on PATH, or Docker Desktop not installed.
            return new DockerCommandResult { Success = false, DockerUnavailable = true };
        }
    }
}
