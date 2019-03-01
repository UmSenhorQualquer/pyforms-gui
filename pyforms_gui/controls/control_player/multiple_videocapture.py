import glob, os, cv2

class MultipleVideoCapture(object):


    def __init__(self, filepath):

        # VideoCapture objects
        self.captures = [cv2.VideoCapture(fn) for fn in self.search_files(filepath)]

        # Number of frames for each VideoCapture
        self.n_frames = [c.get(7) for c in self.captures]

        # Total frames ranges starting in 0
        self.frames_ranges = [0]

        # Active VideoCapture
        self.capture_index = 0

        for cap in self.captures:
            nframes = self.frames_ranges[-1]+int(cap.get(7))
            self.frames_ranges.append(nframes)

    @classmethod
    def search_files(cls, filepath):
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        if name.endswith('_1') or name.endswith('_01'):
            names = name.rsplit('_', 1)
            search_name = os.path.join(filedir, names[0] + '_*' + ext)
            return sorted(glob.glob(search_name))
        else:
            return []

    @property
    def capture(self):
        return self.captures[self.capture_index]

    def read(self):
        next_capture = self.capture.get(1)==self.n_frames[self.capture_index]
        if next_capture:
            self.capture_index += 1
            self.capture.set(1,0)
        res = self.capture.read()
        return res


    def get(self, flag):
        if flag==1:
            return self.frames_ranges[self.capture_index]+int(self.capture.get(1))
        elif flag==7:
            # Return the total of frames
            return self.frames_ranges[-1]
        else:
            return self.capture.get(flag)

    def set(self, flag, value):

        if flag==1:
            for index, nframes in enumerate(self.frames_ranges):
                if nframes<value:
                    self.capture_index = index

            self.capture.set(flag, value-self.frames_ranges[self.capture_index])
        else:
            self.capture.set(flag, value)




if __name__ == "__main__":

    video = MultipleVideoCapture('/home/ricardo/bitbucket/idtracker-project/idtrackerai_video_example_01.avi')