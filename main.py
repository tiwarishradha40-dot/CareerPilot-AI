def get_video_details():
    print("=" * 50)
    print("           AI CONTENT STUDIO")
    print("=" * 50)

    # Get video topic
    topic = input("\nEnter your video topic: ").strip()

    while not topic:
        print("Error: Topic cannot be empty.")
        topic = input("Enter your video topic: ").strip()

    # Get target country
    country = input("Enter your target country: ").strip()

    while not country:
        print("Error: Target country cannot be empty.")
        country = input("Enter your target country: ").strip()

    # Get video duration
    duration = input("Enter video duration (in minutes): ").strip()

    while not duration.isdigit() or int(duration) <= 0:
        print("Error: Duration must be a positive number.")
        duration = input("Enter video duration (in minutes): ").strip()

    return topic, country, duration


def create_content_brief(topic, country, duration):
    brief = {
        "topic": topic,
        "target_audience": country,
        "duration": duration,
        "content_goal": "Create an engaging video for the target audience.",
        "structure": [
            "Hook",
            "Introduction",
            "Main Content",
            "Interesting Facts",
            "Conclusion",
            "Call to Action"
        ]
    }

    return brief


def display_content_brief(brief):
    print("\n" + "=" * 50)
    print("           CONTENT BRIEF")
    print("=" * 50)

    print("\nTopic:", brief["topic"])
    print("Target Audience:", brief["target_audience"])
    print("Video Duration:", brief["duration"], "minutes")

    print("\nContent Goal:")
    print(brief["content_goal"])

    print("\nSuggested Structure:")

    for number, section in enumerate(brief["structure"], start=1):
        print(f"{number}. {section}")

    print("\n" + "=" * 50)
    print("AI Content Studio is ready!")
    print("=" * 50)


def main():
    topic, country, duration = get_video_details()

    brief = create_content_brief(
        topic,
        country,
        duration
    )

    display_content_brief(brief)


if __name__ == "__main__":
    main()