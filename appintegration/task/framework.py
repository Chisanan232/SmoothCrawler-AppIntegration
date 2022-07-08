from typing import Any, Optional, Iterable
from abc import ABCMeta, ABC, abstractmethod



class ApplicationIntegrationTask(metaclass=ABCMeta):

    @abstractmethod
    def init(self, *args, **kwargs) -> Any:
        pass


    @abstractmethod
    def close(self) -> None:
        pass



class ApplicationIntegrationSourceTask(ApplicationIntegrationTask, ABC):

    @abstractmethod
    def generate(self, data: Iterable[Iterable]) -> Optional[Any]:
        pass



class ApplicationIntegrationProcessorTask(ApplicationIntegrationTask, ABC):

    @abstractmethod
    def acquire(self, **kwargs) -> Optional[Any]:
        pass

