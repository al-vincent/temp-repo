"""Automatic summarisation of passages of text, using pre-trained Transformers from
https://huggingface.co/models  These models are freely available and have been 
trained on a large number of article/summary pairs (generally from news stories).

Can be run either from the command line as a script, or imported via the TextSummariser
class. To run as a standalone script, use
> python text_summariser

A series of CLI arguments are also included; to view these, use
> python text_summariser -- help
"""

# =====================================================================================
# Import libraries
# =====================================================================================
import click
import torch
from transformers import pipeline


# =====================================================================================
# Constants
# =====================================================================================
EXAMPLE_TEXT = """One month after the United States began what has become a troubled 
rollout of a national COVID vaccination campaign, the effort is finally gathering real 
steam. Close to a million doses -- over 951,000, to be more exact -- made their way 
into the arms of Americans in the past 24 hours, the U.S. Centers for Disease Control 
and Prevention reported Wednesday. That's the largest number of shots given in one day 
since the rollout began and a big jump from the previous day, when just under 340,000 
doses were given, CBS News reported. That number is likely to jump quickly after the 
federal government on Tuesday gave states the OK to vaccinate anyone over 65 and said 
it would release all the doses of vaccine it has available for distribution. Meanwhile,
a number of states have now opened mass vaccination sites in an effort to get larger 
numbers of people inoculated, CBS News reported."""


# =====================================================================================
# Import libraries
# =====================================================================================
class TextSummariser:
    """Setup and run the automated text summarisation. 

    Attributes:
        text (str): the original text to be summarised 
        num_words (int): the number of words in the original text (approx)
        min_percent (float): the percentage of num_words to use as a lower bound for 
            the summary. I.e. lower bound = int(num_words * min_percent)
        max_percent (float): the percentage of num_words to use as an upper bound for 
            the summary. I.e. lower bound = int(num_words * min_percent)
        bounds (tuple): the lower and upper bounds for the length of the summary. 
            bounds[0] = lower bound, bounds[1] = upper bound
        model (str): the name of the Hugging Face model to use, from 
            https://huggingface.co/models
        num_beams (int): the number of beams to use for beam search across the model.
            More beams provides a higher-probability output, but takes longer to run.
        n_grams (int): value for no-repeat-n-grams; i.e. phrases of n words that can't
            be repeated in the summary. Min is 2.

    Methods:
        set_summary_bounds: if summary bounds have not been provided, set values using
            defaults. If summary bounds have been provided, undertake some simple error 
            and consistency checking.
        run_summariser: setup and run the summariser, returning the summary.
    """
    def __init__(self, text, bounds=None, min_percent=0.1, max_percent=0.8, 
                model="sshleifer/distilbart-cnn-12-6", num_beams=10, n_grams=3):
        self.text = text
        self.num_words = len(text.split())
        self.min_percent = min_percent
        self.max_percent = max_percent
        self.bounds = self.set_summary_bounds(bounds)
        self.model = model
        self.num_beams = num_beams
        self.n_grams = n_grams

    def set_summary_bounds(self, summary_bounds):
        """If the min and max lengths for the summary are not set, calculate some
        loose bounds based on the number of words in the original text.

        If min and max lengths *have* been provided, do some basic checks to ensure the
        format and values are appropriate.

        Parameters:
            summary_bounds (tuple), the upper and lower bounds for the length of the
                summarised text. Of the form (lower_bound (int), upper_bound (int))

        Returns: 
            tuple: form of (int1, int2) where int1 = min number of words in summary and
                int2 = max number of words in summary

        Raises:
            TypeError: raised if the summary_bounds parameter is not a tuple, or None
            ValueError: raised if the summary_bounds parameter is a tuple, but does not 
                have two items.
            ValueError: raised if the first item of summary_bounds is not less than the 
                second item
            ValueError: raised if the lower bound for the summary length is greater 
                than the total number of words in the original text. 
                NOTE: if the upper bound for the summary is greater than the original 
                document, an error is *not* raised, as the summary algorithm will 
                handle this.
        """
        if summary_bounds is not None:
            # check that summary_bounds is a tuple
            if not isinstance(summary_bounds, tuple):
                raise TypeError(
                    "Variable summary_bounds should be of type 'tuple', "
                    f"but type is {type(summary_bounds)}"
                )
            # check that the tuple has exactly two items
            elif len(summary_bounds) != 2:
                raise ValueError(
                    "Variable summary_bounds should have 2 items, but "
                    f"has {len(summary_bounds)} items; {summary_bounds}"
                )
            # check that the 1st item (lower bound) is <= 2nd item (upper bound)
            elif summary_bounds[0] >= summary_bounds[1]:
                raise ValueError(
                    f"The lower bound, {summary_bounds[0]}, should be "
                    f"smaller than the upper bound {summary_bounds[1]}"
                )
            # check that the lower bound is less than the number of words in the
            # original text
            elif summary_bounds[0] > self.num_words:
                raise ValueError(
                    f"The lower bound, {summary_bounds[0]}, should be less than the "
                    f" number of words in the text, {self.num_words}"
                )
            # if all of the above are true, return the bounds unchanged
            else:
                return summary_bounds
        else:
            # set default (min, max) values to be (10%, 80%) of number of words in
            # original text.
            min_wds = int(self.num_words * self.min_percent)
            max_wds = int(self.num_words * self.max_percent)
            return (min_wds, max_wds)


    def run_summariser(self):
        """Set up and run the summariser, using the settings provided to the class.

        Returns:
            str: the summary generated by the model.
        """
        # Find out whether there's a CUDA GPU available. If so, use it; otherwise,
        # use CPU
        device = 0 if torch.cuda.is_available() else -1
        print(f"Processor: {'CUDA' if device == 0 else 'CPU'}")

        # Set up the pipeline and perform the summarisation
        try:
            summariser = pipeline("summarization", model=self.model, device=device)
        except Exception as err:
            print(f"{err}. Could not produce summary.")
        else:
            summary = summariser(
                self.text,
                min_length=self.bounds[0],
                max_length=self.bounds[1],
                clean_up_tokenization_spaces=True
            )[0]['summary_text'].strip()

            # Return the summary generated
            return summary


# =====================================================================================
# Helper functions
# =====================================================================================
def get_text_to_summarise(path=None):
    """Function to read text from a file (e.g. a .txt file) for processing by 
    TextSummariser. If not provided, function returns the example text to demo the
    functionality.

    Parameters:
        path (str, optional): Path to the file whose contents will be read. Defaults to
        None.

    Returns:
        str: the text to be summarised, either read from a file or using example text.
    """
    if not path:
        print(f"*** WARNING: no filepath provided, using example text ***\n")
    else:
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError as err:
            print(f"*** ERROR: {err} ***")
    
    return EXAMPLE_TEXT

def print_details(bounds, model, num_beams, n_grams, text, summary):
    """Convenience function to print model settings and outputs to the console.

    Parameters:
        settings (_type_): _description_
    """
    # Print model settings
    print(f"\nSettings: \n{'-' * 8}")
    print(f"Model: {model}")
    print(f"Min summary length: {bounds[0]}")
    print(f"Max summary length: {bounds[1]}")
    print(f"Number of beams: {num_beams}")
    print(f"No-repeat n-grams: {n_grams}")

    # Print original text
    print(f"\nOriginal text: \n{'-' * 13}")
    print(text.replace("\n", ""))

    # Print summary text
    print(f"\nSummary: \n{'-' * 7}")
    print(summary)


# =====================================================================================
# Drivers
# =====================================================================================
# Add CLI arguments 
@click.command(context_settings={'show_default': True})
@click.option("--path", default="", type=str,
            help="Path to the file containing the text to be summarised. If not "
                "provided, some example text will be used.")
@click.option("--bounds", default=[], type=tuple,
            help="Tuple that defins the min and max lengths of the summary to be "
                "generated. If not provided, default values will be calculated.")
@click.option("--model", default="sshleifer/distilbart-cnn-12-6", type=str,
            help="The huggingface model to use for summarisation (see "
                "https://huggingface.co/models).")
@click.option("--num_beams", default=10, type=int,
            help="The number of beams to use for beam search in the summary.")
@click.option("--n_grams", default=3, type=int,
            help="The length of n-grams that shouldn't be repeated in the summary.")           
# Run the driver            
def main(path, bounds, model, num_beams, n_grams):
    """Driver function to demonstrate use of the TextSummariser class. Uses a series of
    CLI arguments to allow parameters to be set. Model settings and results are printed
    to the console.

    Parameters:
        path (str): Path to the file whose contents will be read. 
        bounds (tuple): the lower and upper bounds for the length of the summary. 
            bounds[0] = lower bound, bounds[1] = upper bound
        model (str): the name of the Hugging Face model to use, from 
            https://huggingface.co/models
        num_beams (int): the number of beams to use for beam search across the model.
            More beams provides a higher-probability output, but takes longer to run.
        n_grams (int): value for no-repeat-n-grams; i.e. phrases of n words that can't
            be repeated in the summary. Min is 2.
    """
    print(f"\n{'='*21}\nRUNNING SUMMARISER...\n")
    path = path if path else None
    bounds = bounds if bounds else None
    model = model if model else None
    text = get_text_to_summarise(path)
    ts = TextSummariser(
        text=text, 
        bounds=bounds,
        model=model, 
        num_beams=num_beams, 
        n_grams=n_grams
    )
    summary = ts.run_summariser()
    
    print_details(ts.bounds, model, num_beams, n_grams, text, summary)
    print(f"\nCOMPLETE\n{'='*8}")

if __name__ == "__main__":
    main()