from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps
from types import MethodType
from typing import Any, Callable, Dict, List, Optional


BeforeAdvice = Callable[[dict], None]
AfterAdvice = Callable[[dict], None]
AroundAdvice = Callable[[Callable[..., Any], tuple, dict, dict], Any]


@dataclass
class AspectSpec:
    before: List[BeforeAdvice] = field(default_factory=list)
    after: List[AfterAdvice] = field(default_factory=list)
    around: List[AroundAdvice] = field(default_factory=list)


class AspectWeaver:
    """
    Baut aspektorientiertes Verhalten in Python nach.

    Unterstützt:
    - before advice
    - after advice
    - around advice
    - patchen freier Funktionen
    - patchen einzelner Objektmethoden
    - patchen kompletter Klassenmethoden

    Kontextschema:
        {
            "target": Zielobjekt oder None,
            "function_name": Name der Funktion/Methode,
            "args": Positionsargumente als tuple,
            "kwargs": Keywordargumente als dict,
            "result": Ergebnis oder None,
            "exception": Exception oder None,
        }
    """

    def __init__(self) -> None:
        self._registry: Dict[str, AspectSpec] = {}

    def register(
        self,
        pointcut: str,
        *,
        before: Optional[BeforeAdvice] = None,
        after: Optional[AfterAdvice] = None,
        around: Optional[AroundAdvice] = None,
    ) -> None:
        spec = self._registry.setdefault(pointcut, AspectSpec())
        if before is not None:
            spec.before.append(before)
        if after is not None:
            spec.after.append(after)
        if around is not None:
            spec.around.append(around)

    def clear(self, pointcut: Optional[str] = None) -> None:
        if pointcut is None:
            self._registry.clear()
        else:
            self._registry.pop(pointcut, None)

    def wrap_function(self, fn: Callable[..., Any], pointcut: str) -> Callable[..., Any]:
        spec = self._registry.get(pointcut)
        if spec is None:
            return fn

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            context = {
                "target": None,
                "function_name": fn.__name__,
                "args": args,
                "kwargs": kwargs,
                "result": None,
                "exception": None,
            }

            for advice in spec.before:
                advice(context)

            def invoke_original(*inner_args: Any, **inner_kwargs: Any) -> Any:
                return fn(*inner_args, **inner_kwargs)

            invocation = invoke_original

            for advice in reversed(spec.around):
                previous = invocation

                def make_layer(
                    current_advice: AroundAdvice,
                    current_previous: Callable[..., Any],
                ) -> Callable[..., Any]:
                    @wraps(current_previous)
                    def layer(*a: Any, **kw: Any) -> Any:
                        return current_advice(current_previous, a, kw, context)

                    return layer

                invocation = make_layer(advice, previous)

            try:
                result = invocation(*args, **kwargs)
                context["result"] = result
                return result
            except Exception as exc:
                context["exception"] = exc
                raise
            finally:
                for advice in spec.after:
                    advice(context)

        return wrapped

    def patch_object_method(self, obj: Any, method_name: str, pointcut: str) -> None:
        original = getattr(obj, method_name)

        # Gebundene Methode eines Objekts patchen
        if hasattr(original, "__func__"):
            fn = original.__func__

            @wraps(fn)
            def wrapped(instance: Any, *args: Any, **kwargs: Any) -> Any:
                spec = self._registry.get(pointcut)
                if spec is None:
                    return fn(instance, *args, **kwargs)

                context = {
                    "target": instance,
                    "function_name": method_name,
                    "args": args,
                    "kwargs": kwargs,
                    "result": None,
                    "exception": None,
                }

                for advice in spec.before:
                    advice(context)

                def invoke_original(*inner_args: Any, **inner_kwargs: Any) -> Any:
                    return fn(instance, *inner_args, **inner_kwargs)

                invocation = invoke_original

                for advice in reversed(spec.around):
                    previous = invocation

                    def make_layer(
                        current_advice: AroundAdvice,
                        current_previous: Callable[..., Any],
                    ) -> Callable[..., Any]:
                        @wraps(current_previous)
                        def layer(*a: Any, **kw: Any) -> Any:
                            return current_advice(current_previous, a, kw, context)

                        return layer

                    invocation = make_layer(advice, previous)

                try:
                    result = invocation(*args, **kwargs)
                    context["result"] = result
                    return result
                except Exception as exc:
                    context["exception"] = exc
                    raise
                finally:
                    for advice in spec.after:
                        advice(context)

            setattr(obj, method_name, MethodType(wrapped, obj))
        else:
            # Fallback für andere Callables
            setattr(obj, method_name, self.wrap_function(original, pointcut))

    def patch_class_method(self, cls: type, method_name: str, pointcut: str) -> None:
        original = getattr(cls, method_name)

        if not callable(original):
            raise TypeError(f"{cls.__name__}.{method_name} ist nicht aufrufbar")

        @wraps(original)
        def wrapped(instance: Any, *args: Any, **kwargs: Any) -> Any:
            spec = self._registry.get(pointcut)
            if spec is None:
                return original(instance, *args, **kwargs)

            context = {
                "target": instance,
                "function_name": method_name,
                "args": args,
                "kwargs": kwargs,
                "result": None,
                "exception": None,
            }

            for advice in spec.before:
                advice(context)

            def invoke_original(*inner_args: Any, **inner_kwargs: Any) -> Any:
                return original(instance, *inner_args, **inner_kwargs)

            invocation = invoke_original

            for advice in reversed(spec.around):
                previous = invocation

                def make_layer(
                    current_advice: AroundAdvice,
                    current_previous: Callable[..., Any],
                ) -> Callable[..., Any]:
                    @wraps(current_previous)
                    def layer(*a: Any, **kw: Any) -> Any:
                        return current_advice(current_previous, a, kw, context)

                    return layer

                invocation = make_layer(advice, previous)

            try:
                result = invocation(*args, **kwargs)
                context["result"] = result
                return result
            except Exception as exc:
                context["exception"] = exc
                raise
            finally:
                for advice in spec.after:
                    advice(context)

        setattr(cls, method_name, wrapped)

    def decorator(self, pointcut: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def inner(fn: Callable[..., Any]) -> Callable[..., Any]:
            return self.wrap_function(fn, pointcut)

        return inner
