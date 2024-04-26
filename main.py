from upload import upload_tx_data
from fetch_emails import extract_email_tx_data

def main() -> None:
    """This function is the main entry point for the program.

    It is responsible for fetching transaction data from emails,
    uploading it to Google Sheets, and handling any errors that may occur.

    The main function does the following:
        - Calls the extract_email_tx_data() function to get the transaction data
        - If there is no transaction data, print a message and return
        - Otherwise, call the upload_tx_data() function to upload the transaction data

    Args:
        None

    Returns:
        None

    """
    try:
        tx_data = extract_email_tx_data()
        if not tx_data:
            print("No new emails to process. Transaction data is empty.")
            return None
        upload_tx_data(tx_data)
    except Exception as error:
        raise Exception(f"Error encountered in main: {error}") from error


if __name__ == "__main__":
    main()