def main():
    """Entry point for the survey agent application."""
    from agent import SurveyAgent

    agent = SurveyAgent()

    def run_survey_generator():
        """Runs the survey generator and enables post-generation edits."""
        
        print("\n" + " SURVEY GENERATOR ".center(100, "=") + "\n")
        
        topic = input("Enter survey topic: ").strip()
        print("Generating survey...")
        survey = agent.generate_survey(topic)
        agent.save_survey(survey, "survey.json")
        
        print("\n" + " Start of Generated Survey ".center(100, "=") + "\n")
        print(survey)
        print("\n" + " End of Generated Survey ".center(100, "=") + "\n")

        while True:
            
            modifications = input("Edit survey: ").strip()
            print("Updating survey...")
            survey = agent.update_survey(survey, modifications)
            agent.save_survey(survey, "survey.json")

            print("\n" + " Start of Generated Survey ".center(100, "=") + "\n")
            print(survey)
            print("\n" + " End of Generated Survey ".center(100, "=") + "\n")

    run_survey_generator()



if __name__ == "__main__":
    main()