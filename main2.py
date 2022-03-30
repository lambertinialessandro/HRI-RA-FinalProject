from modules.AudioStreamModule import ComputerMicrophoneStream

audio = ComputerMicrophoneStream()

while True:
    a = audio.get_stream_word()
    print(a)
