class Redactcli < Formula
  include Language::Python::Virtualenv

  desc "Redact secrets from agent output, logs, diffs, and CI"
  homepage "https://github.com/AshSgDe29071999/redactcli"
  url "https://files.pythonhosted.org/packages/6f/1d/0dcccc3b137e1a85db982a72c6c41a98013af7ad3cad5e21fe74450a94f8/redactcli-0.1.0.tar.gz"
  sha256 "b48feeac70886f165022db6fe504533a3d7c4423c8e199fcbcb4e2467606368a"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/redactcli --version")
    output = pipe_output("#{bin}/redactcli", "token=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab\n")
    assert_match "REDACTED", output
    refute_match(/ghp_[A-Za-z0-9]{20,}/, output)
  end
end
