import logging

# imports for supported template functions
# f'QED{dateparse("today").strftime("%Y%m%d")}'
from dateparser import parse as dateparse  #noqa:F401

from . import Instruction

log = logging.getLogger("InstructionTemplate")

class InstructionTemplate(Instruction):
    pass

    def get_command(self):
        try:
            _command = eval(self.command_str)
            log.debug("eval'd command_str to %s", _command)
            return _command
        except SyntaxError as ex:
            print(ex)
            return
        
        


# log.debug("got a templated command: %s", command_str)
#         # Process templated command type
#         template = command_str
#         
#             code = eval(template)  # pylint: disable=W0123

        # # re-eval template if needed
        # if self.command_type == 'templated':
        #     log.debug("updating templated command: %s", self.template)
        #     try:
        #         self.code = eval(self.template)  # pylint: disable=W0123
        #         log.info("templated command now: %s", self.code)
        #         # print(self.template)
        #         # print(self.code)
        #     except SyntaxError as ex:
        #         print(ex)
        #         return
#         