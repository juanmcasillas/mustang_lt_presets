import time
import ltamp

amp = ltamp.LtAmp()
amp.connect()
amp.send_sync_begin()
amp.send_sync_end()
amp.set_preset(60)
amp.set_qa_slots([1,2])
amp.request_firmware_version()
for i in range(5):
    amp.send_heartbeat()
    print(amp.request_qa_slots())
    time.sleep(1)
amp.disconnect()