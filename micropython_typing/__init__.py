class _TypeHint:
    def __getitem__(self, value) -> ...:
        ...


__type_hint = _TypeHint()

Annotated = __type_hint
Any = __type_hint
Callable = __type_hint
ClassVar = __type_hint
Concatenate = __type_hint
Final = __type_hint
ForwardRef = __type_hint
Generic = __type_hint
Literal = __type_hint
Optional = __type_hint
ParamSpec = __type_hint
Protocol = __type_hint
Tuple = __type_hint
Type = __type_hint
TypeVar = __type_hint
TypeVarTuple = __type_hint
Union = __type_hint

# ABCs (from collections.abc).
AbstractSet = __type_hint  # collections.abc.Set.
ByteString = __type_hint
Container = __type_hint
ContextManager = __type_hint
Hashable = __type_hint
ItemsView = __type_hint
Iterable = __type_hint
Iterator = __type_hint
KeysView = __type_hint
Mapping = __type_hint
MappingView = __type_hint
MutableMapping = __type_hint
MutableSequence = __type_hint
MutableSet = __type_hint
Sequence = __type_hint
Sized = __type_hint
ValuesView = __type_hint
Awaitable = __type_hint
AsyncIterator = __type_hint
AsyncIterable = __type_hint
Coroutine = __type_hint
Collection = __type_hint
AsyncGenerator = __type_hint
AsyncContextManager = __type_hint

# Structural checks, a.k.a. protocols.
Reversible = __type_hint
SupportsAbs = __type_hint
SupportsBytes = __type_hint
SupportsComplex = __type_hint
SupportsFloat = __type_hint
SupportsIndex = __type_hint
SupportsInt = __type_hint
SupportsRound = __type_hint

# Concrete collection types.
ChainMap = __type_hint
Counter = __type_hint
Deque = __type_hint
Dict = __type_hint
DefaultDict = __type_hint
List = __type_hint
OrderedDict = __type_hint
Set = __type_hint
FrozenSet = __type_hint
NamedTuple = __type_hint  # Not really a type.
TypedDict = __type_hint  # Not really a type.
Generator = __type_hint

# Other concrete types.
BinaryIO = __type_hint
IO = __type_hint
Match = __type_hint
Pattern = __type_hint
TextIO = __type_hint

# One-off things.
AnyStr = __type_hint
assert_type = __type_hint
assert_never = __type_hint
cast = __type_hint
clear_overloads = __type_hint
dataclass_transform = __type_hint
final = __type_hint
get_args = __type_hint
get_origin = __type_hint
get_overloads = __type_hint
get_type_hints = __type_hint
is_typeddict = __type_hint
LiteralString = __type_hint
Never = __type_hint
NewType = __type_hint
no_type_check = __type_hint
no_type_check_decorator = __type_hint
NoReturn = __type_hint
NotRequired = __type_hint
overload = __type_hint
ParamSpecArgs = __type_hint
ParamSpecKwargs = __type_hint
Required = __type_hint
reveal_type = __type_hint
runtime_checkable = __type_hint
Self = __type_hint
Text = __type_hint
TYPE_CHECKING = __type_hint
TypeAlias = __type_hint
TypeGuard = __type_hint
Unpack = __type_hint
