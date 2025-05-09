
class ProgressBarLibary:
    def  progress_bar(self, title, progress, total):
        percent = 100 * (progress / float(total))
        bar = '█' * int(percent) + '-' * (100 - int(percent))
        print(f"\r{title} |{bar}| {percent:.2f}% ({progress}/{total})", end="")