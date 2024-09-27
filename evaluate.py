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
import random
import multiprocessing
import multiprocessing.pool
# from multiprocessing import Pool
from statistics import mean
from pathlib import Path
from pprint import pformat, pprint
from image_metrics import ImageMetrics
from segmentation_metrics import SegmentationMetrics


INPUT_DIRECTORY = Path("/input")
OUTPUT_DIRECTORY = Path("/output")
GROUND_TRUTH_DIRECTORY = Path("ground_truth")



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


def main():
    print_inputs()

    metrics = {}
    predictions = read_predictions()

    # We now process each algorithm job for this submission
    # Note that the jobs are not in any order!
    # We work that out from predictions.json

    # Start a number of process workers, using multiprocessing
    # The optimal number of workers ultimately depends on how many
    # resources each process() would call upon

    metrics['results'] = []
    # for p in predictions:
    #     metrics['results'].append(process(p))
    with NestablePool(processes=4) as pool:
        metrics["results"] = pool.map(process, predictions)

    print(metrics)
    # Now generate an overall score(s) for this submission
    metrics["aggregates"] = {}# "my_metric": mean(result["my_metric"] for result in metrics["results"])
    
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
    mri_image = get_file_location(
            job_pk=job["pk"],
            values=job["inputs"],
            slug="mri-image",
        )
    

    # Secondly, read the results
    # retinal_vessel_segmentation = load_image_file(
    #     location=retinal_vessel_segmentation_location,
    # )
    


    # Thirdly, retrieve the input image name to match it with an image in your ground truth
    base_file_name = get_image_name(
            values=job["inputs"],
            slug="mri-image",
    )    

    # Fourthly, your load your ground truth
    # Include it in your evaluation container by placing it in ground_truth/

    # gt_img = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(GROUND_TRUTH_DIRECTORY / "ct" / base_file_name))
    # mask = SimpleITK.GetArrayFromImage(SimpleITK.ReadImage(GROUND_TRUTH_DIRECTORY / "mask" / base_file_name))


    ground_truth_path = GROUND_TRUTH_DIRECTORY / "ct" / base_file_name
    mask_path = GROUND_TRUTH_DIRECTORY / "mask" / base_file_name
    segmentation_path = GROUND_TRUTH_DIRECTORY / "mask" / base_file_name

    image_evaluator = ImageMetrics()
    image_metrics = image_evaluator.score_patient(ground_truth_path, ground_truth_path, mask_path)
    print(image_metrics)

    segmentation_evaluator = SegmentationMetrics()
    seg_metrics = segmentation_evaluator.score_patient(ground_truth_path, ground_truth_path, mask_path, segmentation_path)
    print(seg_metrics)

    # Finally, calculate by comparing the ground truth to the actual results
    return {
        **image_metrics,
        **seg_metrics
    }


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


def get_file_location(*, job_pk, values, slug):
    # Where a job's output file will be located in the evaluation container
    relative_path = get_interface_relative_path(values=values, slug=slug)
    return INPUT_DIRECTORY / job_pk / "output" / relative_path


def load_image_file(*, location):
    # Use SimpleITK to read a file
    print("LCOATION", location)
    input_files = glob(str(location / "*.nii.gz")) + glob(str(location / "*.tiff")) + glob(str(location / "*.mha"))
    result = SimpleITK.ReadImage(input_files[0])

    # Convert it to a Numpy array
    return SimpleITK.GetArrayFromImage(result)


def write_metrics(*, metrics):
    # Write a json document used for ranking results on the leaderboard
    with open(OUTPUT_DIRECTORY / "metrics.json", "w") as f:
        f.write(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    raise SystemExit(main())
