# coding: utf-8

Gem::Specification.new do |spec|
  spec.name          = "jekyll-theme-hydeout-0x41cf"
  spec.version       = "0.0.1"
  spec.authors       = ["Andrew Fong, Sami Alaoui Kendil, Jacob Garrison"]
  spec.email         = ["contact@j4ke.io"]

  spec.summary       = %q{The Hyde theme for Jekyll.}
  spec.homepage      = "https://github.com/j4ke-exe/j4ke.io"
  spec.license       = "MIT"

  spec.metadata["plugin_type"] = "theme"

  spec.files         = `git ls-files -z`.split("\x0").select do |f|
    f.match(%r{^(assets|_(includes|layouts|sass)/|(LICENSE|README)((\.(txt|md|markdown)|$)))}i)
  end

  spec.bindir        = "exe"
  spec.executables   = spec.files.grep(%r{^exe/}) { |f| File.basename(f) }

  spec.add_runtime_dependency "jekyll", "~> 4.3.2"
  spec.add_runtime_dependency "jekyll-gist", "~> 1.4"
  spec.add_runtime_dependency "jekyll-paginate", "~> 1.1"
  spec.add_runtime_dependency "jekyll-feed", "~> 0.6"
  spec.add_runtime_dependency "jekyll-timeago", "~> 0.14.0"
  spec.add_runtime_dependency "nokogiri", ">= 1.11.7", "< 1.14.0"
  spec.add_development_dependency "bundler", "~> 2.2.13"
end
