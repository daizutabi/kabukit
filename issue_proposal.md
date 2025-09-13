### **Title (新戦略版)**

`Feature Request: Add async iterable support to mo.status.progress_bar`

### **Body (新戦略版)**

First, I'd like to acknowledge the fantastic work being done in **PR #6304** to improve support for synchronous iterators and fix the type hints for `mo.status.progress_bar`.

As a natural next step to build upon that foundation, I propose adding support for **asynchronous iterables**.

This would complete the feature, making `progress_bar` a truly universal tool for tracking the progress of any iteration, sync or async.

#### Proposed Solution

This can be achieved by implementing the `__aiter__` method on the `progress_bar` class, in addition to the changes being made in PR #6304.

A potential implementation could look like this:

```python
async def __aiter__(self) -> AsyncIterator[S]:
    # Assumes self.iterable is set to an async iterable in __init__
    async for item in self.iterable:
        yield item
        if not self.disabled:
            self.progress.update(increment=self.step)
    self._finish()
```

This would enable `progress_bar` to work seamlessly with `async for` loops, greatly improving the developer experience for async workflows in marimo.

The ideal usage would then look like this:

```python
# Synchronous generators
for i in mo.status.progress_bar(my_generator(), total=10):
    ...

# Asynchronous generators (enabled by this proposal):
async for i in mo.status.progress_bar(my_async_generator(), total=10):
    ...
```

#### Plan for Contribution

To keep the concerns separated and respect the ongoing work, I would like to propose the following plan:

1. PR #6304 (synchronous support) is reviewed and merged first.
2. After that, I will create a new pull request to implement this async support (`__aiter__`).

This ensures a smooth, step-by-step enhancement to the `progress_bar` component.
