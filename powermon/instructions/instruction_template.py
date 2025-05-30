from . import Instruction

class InstructionTemplate(Instruction):
    @classmethod
    def from_config(cls, config):
        print('Instruction template todo')
        return cls


# log.debug("got a templated command: %s", command_str)
#         # Process templated command type
#         template = command_str
#         try:
#             code = eval(template)  # pylint: disable=W0123
#         except SyntaxError as ex:
#             print(ex)
#             return