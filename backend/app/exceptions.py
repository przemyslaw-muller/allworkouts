'''Custom exceptions for AllWorkouts backend'''


class ParserException(Exception):
    '''Base exception for parser errors'''

    pass


class LLMException(ParserException):
    '''Exception for LLM-related errors'''

    pass


class ExerciseMatchException(ParserException):
    '''Exception for exercise matching errors'''

    pass
