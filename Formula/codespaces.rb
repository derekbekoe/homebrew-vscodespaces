# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
class Codespaces < Formula
  desc "Visual Studio Codespaces Self-Hosted Agent"
  homepage "https://online.visualstudio.com"
  # We do not specify `version "..."` as 'brew audit' will complain - see https://github.com/Homebrew/legacy-homebrew/issues/32540
  url "https://vsoagentdownloads.blob.core.windows.net/vsoagent/VSOAgent_osx_3958053.zip"
  # must be lower-case
  sha256 "a50ccdbcd94069a02f5f78309c314c6347b4ac007bf5c8258c551b6ee03d2649"
  bottle :unneeded

  # .NET Core 3.1 requires High Sierra - https://docs.microsoft.com/en-us/dotnet/core/install/dependencies?pivots=os-macos&tabs=netcore31
  depends_on macos: :high_sierra

  def install
    libexec.install Dir["*"]
    chmod 0555, libexec/"codespaces"
    chmod 0555, libexec/"vsls-agent"
    bin.install_symlink libexec/"codespaces"
  end

  def caveats
    <<~EOS
      The executable should already be on PATH so run with `codespaces`. If not, the full path to the executable is:
        #{bin}/codespaces

      Other application files were installed at:
        #{libexec}
    EOS
  end

  test do
    system bin/"codespaces"
    system bin/"codespaces", "--help"
    system bin/"codespaces", "--version"
  end
end
