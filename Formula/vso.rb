# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
class Vso < Formula
  desc "Visual Studio Online Self-Hosted Agent"
  homepage "https://online.visualstudio.com"
  # We do not specify `version "..."` as 'brew audit' will complain - see https://github.com/Homebrew/legacy-homebrew/issues/32540
  url "https://vsoagentdownloads.blob.core.windows.net/vsoagent/VSOAgent_osx_3669160.zip"
  # must be lower-case
  sha256 "d515f5372a621be23b3acea70496e83b3bd8650faa9471e351befca7798fd4ce"
  bottle :unneeded

  # .NET Core 3.1 requires High Sierra - https://docs.microsoft.com/en-us/dotnet/core/install/dependencies?pivots=os-macos&tabs=netcore31
  depends_on :macos => :high_sierra

  def install
    libexec.install Dir["*"]
    chmod 0555, libexec/"vso"
    chmod 0555, libexec/"vsls-agent"
    bin.install_symlink libexec/"vso"
  end

  def caveats
    <<~EOS
      The executable should already be on PATH so run with `vso`. If not, the full path to the executable is:
        #{bin}/vso

      Other application files were installed at:
        #{libexec}
    EOS
  end

  test do
    system bin/"vso"
    system bin/"vso", "--help"
    system bin/"vso", "--version"
  end
end
