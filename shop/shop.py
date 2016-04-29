import logging


class SymbolMeta(type):
    def __getattr__(cls, name):
        if name.startswith("__"):
            super(SymbolMeta, type).__getattr__(name)
        return cls(name=name)


class KResult(dict):
  pass


class DictCombiner(object):
  def __repr__(self):
    return "(%s + %s)" % (self.left, self.right)

  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __call__(self, obj):
    def merge(child, self_result):
      child_result = child(obj)
      if isinstance(child_result, KResult):
        return dict(self_result.items() + child_result.items())
      else:
        return dict(self_result.items() + [(child._path(), child_result)])

    self_result = KResult()
    self_result = merge(self.left, self_result)
    self_result = merge(self.right, self_result)
    return self_result

  def __add__(self, other):
    return DictCombiner(self, other)


class k(object):
    __metaclass__ = SymbolMeta

    def __repr__(self):
        chain = self._chain()
        names = [k_.name for k_ in chain]
        return "k<%s>" % ".".join(names)

    def __init__(self, name=None, prev=None):
        self.name = name
        self.prev = prev

    def __getattr__(self, name):
        return k(name=name, prev=self)

    def __call__(self, obj):
        if self.prev:
            res = self.prev(obj)
        else:
            res = obj
        logging.debug(str(self), res)
        if res is not None:
            if self.name == "_":
              return res
            attr_or_none = getattr(res, self.name, None)
            if attr_or_none is None and hasattr(res, '__getitem__'):
                attr_or_none = res.get(self.name, None)
            return attr_or_none
        else:
            return res

    def _chain(self):
        if self.prev:
            return self.prev._chain() + [self]
        else:
            return [self]

    def _path(self):
        chain = self._chain()
        names = [k_.name for k_ in chain]
        return "%s" % "_".join(names)

    def __add__(self, other):
        return DictCombiner(self, other)
