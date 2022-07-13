from smoothcrawler_appintegration.task.framework import (
    ApplicationIntegrationSourceTask,
    ApplicationIntegrationProcessorTask
)

from typing import Iterable, Any, Union, TypeVar, Generic
from abc import ABCMeta, abstractmethod
import traceback
import pytest
import os


_AppIntegrationTask = Union[ApplicationIntegrationSourceTask, ApplicationIntegrationProcessorTask]
_AppIntegrationTaskGeneric = TypeVar("_AppIntegrationTaskGeneric", bound=_AppIntegrationTask)


class AppIntegrationTaskTestSpec(metaclass=ABCMeta):

    @pytest.fixture(scope="class")
    def task(self) -> Generic[_AppIntegrationTaskGeneric]:
        """
        Which **Task** object it would be tested. It would be refresh (re-instantiate) in different classes.
        The different between this and *task_for_generating*, *task_for_acquiring* is this function would
        be the default of others. It means that if it doesn't override *task_for_generating*, *task_for_acquiring*,
        these 2 functions would return *task* value. Conversely, it could return the specific instance for
        generating or acquiring if it needs by overriding these functions *task_for_generating*, *task_for_acquiring*.

        :return: Returns the *ApplicationIntegrationTask* instance to test.
        """

        return None


    @pytest.fixture(scope="class")
    def task_for_generating(self, task: _AppIntegrationTask) -> Generic[_AppIntegrationTaskGeneric]:
        """
        Which *Task* it would test for. This task instance only for generating feature.

        :param task: The default value for this function. In must to be the *ApplicationIntegrationTask* instance.
        :return: Returns the *ApplicationIntegrationSourceTask* instance to test.
        """

        return task


    @pytest.fixture(scope="class")
    def task_for_acquiring(self, task: _AppIntegrationTask) -> Generic[_AppIntegrationTaskGeneric]:
        """
        Which *Task* it would test for. This task instance only for acquiring feature.

        :param task: The default value for this function. In must to be the *ApplicationIntegrationTask* instance.
        :return: Returns the *ApplicationIntegrationProcessorTask* instance to test.
        """

        return task


    def test_generate(self, task_for_generating: _AppIntegrationTask) -> None:
        """
        The truly implementation of generating feature usage.
        The running procedure is:

            Run the implementation -> Check the running result -> Run some processes finally

        * Run the implementation: test_generate
        * Check the running result: _chk_generate_running_result
        * Run some processes finally: _chk_generate_final_ps

        :param task_for_generating: The instance of *ApplicationIntegrationSourceTask*.
        :return: None
        """

        # Get data
        _data = self._testing_data()

        # Run the major feature for source App
        try:
            task_for_generating.init()
            task_for_generating.generate(data=_data)
            task_for_generating.close()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        # Check the running result
        self._chk_generate_running_result()
        self._chk_generate_final_ps()


    @abstractmethod
    def _testing_data(self) -> Union[Iterable[Iterable], Any]:
        """
        The data for testing generating (writing data to file, database, send to another connection or message middle component) feature.

        :return: The testing data. In generally, it should be iterable type.
        """

        pass


    @abstractmethod
    def _chk_generate_running_result(self, **kwargs) -> None:
        """
        The checking of running result of generating.

        ..Note:
        It has a little bit special usage of this feature is you must to implement it and
        call the father-class's function with option *file_path*. For example:

            super(TestTask, self)._chk_generate_running_result(file_path=Test_File_Path)

        It should get the *file_path* value by sub-class's function.

        :return: None
        """

        _file_path = kwargs.get("file_path", None)
        assert _file_path is not None, "The file path should NOT be None value."
        _exist_file = os.path.exists(_file_path)
        assert _exist_file is True, "It should exist a file."


    def _chk_generate_final_ps(self, **kwargs) -> None:
        """
        The final process it would be work after others running for generating test.

        :return: None
        """

        self._chk_final_ps(**kwargs)


    def test_acquire(self, task_for_acquiring: _AppIntegrationTask) -> None:
        """
        The truly implementation of acquiring feature usage.
        The running procedure is:

            Run the implementation -> Check the running result -> Run some processes finally

        * Run the implementation: test_acquire
        * Check the running result: _chk_acquire_running_result
        * Run some processes finally: _chk_acquire_final_ps

        :param task_for_acquiring: The instance of *ApplicationIntegrationProcessorTask*.
        :return: None
        """

        try:
            task_for_acquiring.init()
            _data = task_for_acquiring.acquire()
            task_for_acquiring.close()
        except Exception:
            assert False, f"It should work finely without any issue.\n The error is: {traceback.format_exc()}"
        else:
            assert True, "It work finely!"

        self._chk_acquire_running_result(data=_data)
        self._chk_acquire_final_ps()


    @abstractmethod
    def _chk_acquire_running_result(self, **kwargs) -> None:
        """
        The checking of running result of acquiring. In generally, it would check whether
        the data it gets (it may read from a file or database table, receive from another
        connection or consume from message middle component) is correct (it should be same
        as it has wrote to file, database or send to another connection or produce to message
        middle component) or not.

        :return: None
        """

        pass


    def _chk_acquire_final_ps(self, **kwargs) -> None:
        """
        The final process it would be work after others running for acquiring test.

        :return: None
        """

        self._chk_final_ps(**kwargs)


    def _chk_final_ps(self, **kwargs) -> None:
        """
        This is the default final function which would be called by *_chk_generate_final_ps*
        and *_chk_acquire_final_ps*.

        :return: None
        """

        pass

