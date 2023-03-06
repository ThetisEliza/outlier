



# T = TypeVar("T", bound=BizReq)

# class BizFunc(Generic[T]):
#     def __init__(self,
#                  fn:        Callable,
#                  command:   str,
#                  atstate:   str,
#                  isrmt:     bool    = False,
#                  cmdptn:    str     = None,
#                  stateto:   State   = 0,
#                  *args, **kwargs) -> None:
#         self._fn        = fn
#         self._command   = command
#         self._atstate   = atstate
#         self._isrmt     = isrmt
#         self._stateto   = stateto
#         self._cmdptn    = cmdptn
#         self._args      = args
#         self._kwargs    = kwargs if kwargs is not None else {}

#     @property
#     def _statusname(self):
#         return f"{self._command}@{self._atstate}"

#     @property
#     def _retname(self):
#         return f"~{self._command}"
    
#     @property
#     def _help(self):
#         usage =  self._kwargs.get("usage", None)
#         usage =  (self._command + ((" "+self._kwargs.get("descparams", "")) if "descparams" in self._kwargs else "")) if usage is None else usage
#         return "\t"+self._command +"\t" + self._kwargs.get("desc", "") + "\n\t\t-Usage:\t" + usage
    
#     def __call__(self, *args: Any, **kwargs: Any) -> Any:
#         return self._fn(*args, **kwargs)
    
#     def __repr__(self) -> str:
#         return f"{self._fn} with {self._command} {self._atstate} {self._isrmt}"

