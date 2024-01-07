from pydub import AudioSegment
import os

thr = -40
dur = 1000


def split_audio(input_file, output_folder, target_duration=3000):
    # Load audio file
    audio = AudioSegment.from_file(input_file) # audiofile을 ms 단위로 나눈다
    print(audio)
    print(len(audio))

    # Find silence regions
    silence_regions = detect_silence(audio, thr, dur)
    print(silence_regions)

    # Create output folder if not exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    stepSum = 0
    # Split audio into segments based on silence regions
    for i in range(len(silence_regions)):
    # for i, (start_time, end_time) in enumerate(silence_regions):

        print(stepSum)
        start_idx = i + stepSum
        print("start", start_idx)

        current_silence = silence_regions[start_idx] if start_idx + 1 < len(silence_regions) else silence_regions[len(silence_regions)-1]
        start_time = current_silence[0]

        # Find the next silence region
        next_silence = silence_regions[start_idx + 1] if start_idx + 1 < len(silence_regions) else (len(audio), len(audio))
        next_next_silence = silence_regions[start_idx + 2] if start_idx + 2 < len(silence_regions) else (len(audio), len(audio))

        adjusted_end_time = next_next_silence[1]
        stepSum = stepSum + 2
        if start_time + target_duration < next_next_silence[1]:
            print("LLL")
            adjusted_end_time = next_silence[1] 
            stepSum = stepSum - 1

        print("end", stepSum)

        # Create the segment
        segment = audio[start_time:adjusted_end_time]

        # Output file path
        output_file = os.path.join(output_folder, f"segment_{i + 1}.wav")

        # Export the segment
        segment.export(output_file, format="wav")

        if i + stepSum > len(silence_regions) - 2:
            break

def detect_silence(audio, silence_threshold=thr, silence_duration=dur):
    silence_regions = []
    print(silence_threshold)

    start_time = None
    for i, sample in enumerate(audio):
        # print(i, " - ", sample.dBFS)
        if sample.dBFS < silence_threshold:
            if start_time is None:
                start_time = i
        elif start_time is not None:
            if i - start_time >= silence_duration:
                silence_regions.append((start_time, i))
                start_time = None

    return silence_regions

if __name__ == "__main__":

    input_file = './data/lip_K_5_M_06_C920_A_001_01.wav'
    output_folder = "./data/splited3"  # Replace with your output folder path
    target_duration = 3000  # Set the target duration in milliseconds (3 seconds)

    split_audio(input_file, output_folder, target_duration)
