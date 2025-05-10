import argparse
from core.job_applicator import JobApplicator
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description='Automate job applications')
    parser.add_argument('--url', type=str, required=True, help='URL of the job posting')
    parser.add_argument('--model', type=str, help='Path to trained model')
    parser.add_argument('--name', type=str, help='Your full name')
    parser.add_argument('--email', type=str, help='Your email address')
    parser.add_argument('--phone', type=str, help='Your phone number')
    parser.add_argument('--address', type=str, help='Your address')
    parser.add_argument('--city', type=str, help='Your city')
    parser.add_argument('--state', type=str, help='Your state')
    parser.add_argument('--zip', type=str, help='Your zip code')
    parser.add_argument('--experience', type=str, help='Your work experience')
    parser.add_argument('--education', type=str, help='Your education')
    parser.add_argument('--skills', type=str, help='Your skills')
    
    args = parser.parse_args()
    
    # Initialize job applicator
    applicator = JobApplicator(model_path=args.model)
    
    # Set application data
    application_data = {
        'name': args.name,
        'email': args.email,
        'phone': args.phone,
        'address': args.address,
        'city': args.city,
        'state': args.state,
        'zip': args.zip,
        'experience': args.experience,
        'education': args.education,
        'skills': args.skills
    }
    
    # Remove empty values
    application_data = {k: v for k, v in application_data.items() if v}
    
    if not application_data:
        logger.error("No application data provided!")
        return
    
    applicator.set_application_data(application_data)
    
    # Apply to the job
    logger.info(f"Applying to job at {args.url}")
    if applicator.apply_to_job(args.url):
        logger.info("Application process completed successfully!")
    else:
        logger.error("Application process failed!")

if __name__ == "__main__":
    main() 