# class AudioCommandRecognition(AbstractCommandRecognition):
#     def __init__(self):
#         super().__init__()
#
#         self.engine = pyttsx3.init()
#         voices = self.engine.getProperty('voices')
#         self.engine.setProperty('voice', voices[1].id)
#
#         self.done = False
#
#     def _talk(self, text):
#         self.engine.say(text)
#         self.engine.runAndWait()
#
#     def get_command(self, text) -> tuple:
#         print("Executing: "+text)
#         # if 'start video' in command:
#         #     self._talk("Video started!")
#         #     return Command.STREAM_ON
#         # elif 'stop video' in command:
#         #     self._talk("Video stopped!")
#         #     return Command.STREAM_OFF
#         # el
#         if self.done or 'turn off' in text:
#             self._talk("Stop execution")
#             return Command.STOP_EXECUTION, None
#         elif 'take off' in text:
#             self._talk("Starting drone! wrwrwr")
#             return Command.TAKE_OFF, None
#         elif 'land' in text:
#             self._talk("Stopping drone! wrwrwr")
#             return Command.LAND, None
#         elif 'follow me' in text:
#             self._talk("i'm following")
#             return Command.FOLLOW_ME, None
#         else:
#             self._talk('Please say the command again.')
#
#         return Command.NONE, None
#
#     def end(self):
#         pass