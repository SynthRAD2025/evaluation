"""
The following is a simple example evaluation method.

It is meant to run within a container.

To run it locally, you can call the following bash script:

  ./test_run.sh

This will start the evaluation, reads from ./test/input and outputs to ./test/output

To export the container and prep it for upload to Grand-Challenge.org you can call:

  docker save example-evaluation-test-phase | gzip -c > example-evaluation-test-phase.tar.gz

Any container that shows the same behavior will do, this is purely an example of how one COULD do it.

Happy programming!
"""
import json
from glob import glob
import SimpleITK
import numpy as np
import random
import multiprocessing
import multiprocessing.pool
# from multiprocessing import Pool
from statistics import mean
from pathlib import Path
from pprint import pformat, pprint
from image_metrics import ImageMetrics
from segmentation_metrics import SegmentationMetrics
import gc

INPUT_DIRECTORY = Path("/input")
OUTPUT_DIRECTORY = Path("/output")
GROUND_TRUTH_DIRECTORY = Path("/opt/ml/input/data/ground_truth")



class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NestablePool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(NestablePool, self).__init__(*args, **kwargs)



def tree(dir_path: Path, prefix: str=''):

    # prefix components:
    space =  '    '
    branch = '│   '
    # pointers:
    tee =    '├── '
    last =   '└── '
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """    
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space 
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)

def main():
    # print_inputs()

    print("INPUT DIR")
    for line in tree(INPUT_DIRECTORY):
        print(line)

    print("")

    print("OUTPUT DIR")
    for line in tree(OUTPUT_DIRECTORY):
        print(line)

    print("")
    print("GT DIR")
    for line in tree(GROUND_TRUTH_DIRECTORY):
        print(line)

    metrics = {}
    predictions = read_predictions()

    # We now process each algorithm job for this submission
    # Note that the jobs are not in any order!
    # We work that out from predictions.json

    # Start a number of process workers, using multiprocessing
    # The optimal number of workers ultimately depends on how many
    # resources each process() would call upon

    metrics['results'] = []
    for p in predictions:
        metrics['results'].append(process(p))
    # with NestablePool(processes=3) as pool:
    #     try:
    #         metrics["results"] = pool.map(process, predictions)
    #     except KeyboardInterrupt:
    #         print('Caught Ctrl+C, shutting pool down...')
    #         pool.terminate()
    #         pool.join()

    print(metrics)
    # Now generate an overall score(s) for this submission
    metrics["aggregates"] = {}# "my_metric": mean(result["my_metric"] for result in metrics["results"])
    
    if len(metrics['results']) > 0:
        for metric in metrics["results"][0].keys():
            metrics["aggregates"][metric] = mean(result[metric] for result in metrics["results"])


    print(metrics)

    # Make sure to save the metrics
    write_metrics(metrics=metrics)

    return 0


def process(job):
    # Processes a single algorithm job, looking at the outputs
    report = "Processing:\n"
    report += pformat(job)
    report += "\n"

    # Firstly, find the location of the results
    synthetic_ct_location = get_file_location(
            job_pk=job["pk"],
            values=job["outputs"],
            slug="synthetic-ct-image",
        )

    # Extract the patient ID
    patient_id = find_patient_id(values=job["inputs"], slug='body')

    # and load the ground-truth along the affine image matrix (Or direction/origin/spacing in SimpleITK terms)
    gt_img, spacing, origin, direction = load_image_file_directly(location=GROUND_TRUTH_DIRECTORY / "ct" / f"{patient_id}.mha", return_orientation=True)

    # Then, read the sCT and impose the spatial dimension of the ground truth
    synthetic_ct, full_sct_path = load_image_file(
        location=synthetic_ct_location, spacing=spacing, origin=origin, direction=direction
    )
    
    # Do the same for the ground-truth TotalSegmentator segmentation and the mask
    gt_segmentation = load_image_file_directly(location=GROUND_TRUTH_DIRECTORY / "segmentation" / f"{patient_id}.mha", set_orientation=(spacing, origin, direction))

    mask = load_image_file_directly(location=GROUND_TRUTH_DIRECTORY / "mask" / f"{patient_id}.mha", set_orientation=(spacing, origin, direction))

    # score the subject based on image metrics
    image_evaluator = ImageMetrics()
    image_metrics = image_evaluator.score_patient(gt_img, synthetic_ct, mask)
    print(patient_id, image_metrics)

    #... and segmentation metrics
    segmentation_evaluator = SegmentationMetrics()
    seg_metrics = segmentation_evaluator.score_patient(full_sct_path, mask, gt_segmentation, patient_id, orientation=(spacing, origin, direction))

    # Finally, return the results
    return {
        **image_metrics,
        **seg_metrics
    }

def find_patient_id(*, values, slug):
    # find the patient id (e.g. TXXXYYY, where T is task (1 or 2), XXX is anatomy and center 
    # (e.g., THC for thorax from center C) and YYY is the patient number (e.g., 001))
    for value in values:
        if value["interface"]["slug"] == slug:
            full_name = value['image']['name'] # this name is like "mask_1ABCxxx.mha"
            return full_name.split('.')[0].split('_')[-1]
    raise RuntimeError(f"Cannot get patient name because interface {slug} not found!")

def print_inputs():
    # Just for convenience, in the logs you can then see what files you have to work with
    input_files = [str(x) for x in Path(INPUT_DIRECTORY).rglob("*.mha") if x.is_file()]

    print("Input Files:")
    pprint(input_files)
    print("")


def read_predictions():
    # The prediction file tells us the location of the users' predictions
    with open(INPUT_DIRECTORY / "predictions.json") as f:
        return json.loads(f.read())


def get_image_name(*, values, slug):
    # This tells us the user-provided name of the input or output image
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["image"]["name"]

    raise RuntimeError(f"Image with interface {slug} not found!")


def get_interface_relative_path(*, values, slug):
    # Gets the location of the interface relative to the input or output
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["interface"]["relative_path"]

    raise RuntimeError(f"Value with interface {slug} not found!")

def get_input_file_location(*, values, slug):
    relative_path = get_interface_relative_path(values=values, slug=slug)
    for value in values:
        if value["interface"]["slug"] == slug:
            full_name = value['image']['name'] # this name is like "mask_1ABCxxx.mha"

            return INPUT_DIRECTORY / relative_path / full_name

    raise RuntimeError(f"Cannot find input file for {slug}!")

def get_file_location(*, job_pk, values, slug):
    # Where a job's output file will be located in the evaluation container
    relative_path = get_interface_relative_path(values=values, slug=slug)
    return INPUT_DIRECTORY / job_pk / "output" / relative_path


def load_image_file_directly(*, location, return_orientation=False, set_orientation=None):
    # immediatly load the file and find its orientation
    result = SimpleITK.ReadImage(location)
    # Note, transpose needed because Numpy is ZYX according to SimpleITKs XYZ
    img_arr = np.transpose(SimpleITK.GetArrayFromImage(result), [2, 1, 0])

    if return_orientation:
        spacing = result.GetSpacing()
        origin = result.GetOrigin()
        direction = result.GetDirection()


        return img_arr, spacing, origin, direction
    else:
        # If desired, force the orientation on an image before converting to NumPy array
        if set_orientation is not None:
            spacing, origin, direction = set_orientation
            result.SetSpacing(spacing)
            result.SetOrigin(origin)
            result.SetDirection(direction)

        # Note, transpose needed because Numpy is ZYX according to SimpleITKs XYZ
        return np.transpose(SimpleITK.GetArrayFromImage(result), [2, 1, 0])


def load_image_file(*, location, spacing=None, origin=None, direction=None):
    # Use SimpleITK to read a file in a directory
    input_files = glob(str(location / "*.nii.gz")) + glob(str(location / "*.tiff")) + glob(str(location / "*.mha"))
    result = SimpleITK.ReadImage(input_files[0])

    if spacing is not None:
        result.SetSpacing(spacing)
    if origin is not None:
        result.SetOrigin(origin)
    if direction is not None:
        result.SetDirection(direction)

    # Convert it to a Numpy array
    return np.transpose(SimpleITK.GetArrayFromImage(result), [2, 1, 0]), input_files[0]


def write_metrics(*, metrics):
    # Write a json document used for ranking results on the leaderboard
    with open(OUTPUT_DIRECTORY / "metrics.json", "w") as f:
        f.write(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    raise SystemExit(main())
