# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
class Vso < Formula
  desc "Visual Studio Online Self-Hosted Agent"
  homepage "https://online.visualstudio.com"
  # We do not specify `version "..."` as 'brew audit' will complain - see https://github.com/Homebrew/legacy-homebrew/issues/32540
  url "https://vsoagentdownloads.blob.core.windows.net/vsoagent/VSOAgent_osx_3883657.zip"
  # must be lower-case
  sha256 "98d7456ec59c7028fa115657c2b2b424b05e868de9937609cae9f1e0b1975005"
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
