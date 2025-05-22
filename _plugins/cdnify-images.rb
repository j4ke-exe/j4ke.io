Jekyll::Hooks.register [:pages, :posts], :pre_render do |post, payload|
  if Jekyll.env == "production"
    docExt = post.extname.tr('.', '')
    if payload['site']['markdown_ext'].include? docExt
      post.content = post.content.gsub(/\[(.*?)\]\((?:{{\s*?site.baseurl\s*?}})?\/assets\/media\/(.*?)\)/, '[\1](https://j4ke.io/assets/media/\2)')
    end
    post.content = post.content.gsub(/(\s(?:src|href))="(?:{{\s*?site.baseurl\s*?}})?\/assets\/media\/(.*?)"/, '\1="https://j4ke.io/assets/media/\2"')
  end
end
