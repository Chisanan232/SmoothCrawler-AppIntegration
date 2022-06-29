from appintegration.role.framework import ApplicationIntegrationRole, MessageQueueRole
from appintegration.task.framework import ApplicationIntegrationTask
from appintegration.task.messagequeue import MessageQueueTask

from typing import TypeVar, Generic
from abc import ABCMeta, abstractmethod
import pytest


_AppIntegrationRole = TypeVar("_AppIntegrationRole", bound=ApplicationIntegrationRole)
_MsgQueueRole = TypeVar("_MsgQueueRole", bound=MessageQueueRole)

_AppIntegrationTask = TypeVar("_AppIntegrationTask", bound=ApplicationIntegrationTask)
_MsgQueueTask = TypeVar("_MsgQueueTask", bound=MessageQueueTask)


class BaseTestSpecConfig(metaclass=ABCMeta):
    """
    This is the configuration for testing items to use. For example, in file based application integration
    case, it needs 2 settings: file path and testing data. So the sub-class of this would add 2 more new
    abstract method: *file_path* and *data*. And in sub-class of **BaseRoleAndTaskTestSpec**, they would
    need to implement a function *spec_config* to let testing items could identify which configuration it
    could use in testing process.
    """

    pass


_BaseTestSpecConfig = TypeVar("_BaseTestSpecConfig", bound=BaseTestSpecConfig)


class BaseRoleAndTaskTestSpec(metaclass=ABCMeta):
    """
    Testing spec for integration test with 2 modules: *role* and *task*.
    """

    @property
    @abstractmethod
    def spec_config(self) -> _BaseTestSpecConfig:
        """
        The configuration object which has some settings testing needs for testing process.

        :return: The instance of sub-class of **BaseTestSpecConfig**.
        """

        pass


    @pytest.fixture(scope="class")
    @abstractmethod
    def task(self) -> Generic[_AppIntegrationRole]:
        """
        One of SUTs and it's sub-class of **ApplicationIntegrationTask** here.

        :return: The instance of sub-class of **ApplicationIntegrationTask**.
        """

        pass


