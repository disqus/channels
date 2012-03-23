Channels
========

Channels was built as a mini-forum for the PyCon 2012 conference as a demo of what can be
achieved through the DISQUS API. Since its inception, the codebase took a turn towards the
more complex, and now represents a reasonable demo of how you can build a write-through cache
(or as we like to call them, materialized views), on top of something like DISQUS.

The site was originally launched on pycon.disqus.com, but is mostly agnostic to its purpose
other than a few chunks of code that are geared towards "sessions".

Caveats
-------

The system works as a valid-forever write-through cache. In the current implementation this
means that if data is changed (or created) outside of the platform, it will never get pushed
into the cache (unless you empty it).