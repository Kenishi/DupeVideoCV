import av
import time 
def scan(filename, progress, skip=5):
	progress.update(filename, 0.00)
	time.sleep(1)
	progress.update(filename, 100.00)

	return (filename, [0,1,2,3])
	# container = av.open(filename)

	# stream = contianer.streams.video[0]
	# stream.codec_context.skip_frame = 'NONKEY'

	# for packet in container.demux(stream):
	# 	for frame in packet.decode():
	# 		progress = round((packet.pos/container.size)*100, 1)
	# 		img = frame.to_ndarray()

	# 		# Calc the descriptors and store the result
	# 		kp, des = surf.detectAndCompute(img, None)
	# 		results.append(des)

	# 		# Update progress
	# 		progressCallback(filename, progress)

	# container.close()