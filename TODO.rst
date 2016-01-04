* decouple backends from the site instance constructor to
  the site instance method `update_pages`.
* decouple `brothers`, `maxdepth`, `blacklist` options from site
  instance constructor to site instance method `fetch_pages` and
  page instance method `fetch_linked_pages`.
* make `update_pages` instance method of `Site` synchronous.
* page fetch filtering option based on distance
