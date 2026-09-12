import sqlite3


def get_video_details():
    print("=" * 50)
    print("           AI CONTENT STUDIO")
    print("=" * 50)

    topic = input("\nEnter your video topic: ").strip()

    while not topic:
        print("Error: Topic cannot be empty.")
        topic = input("Enter your video topic: ").strip()

    country = input("Enter your target country: ").strip()

    while not country:
        print("Error: Target country cannot be empty.")
        country = input("Enter your target country: ").strip()

    duration = input("Enter video duration (in minutes): ").strip()

    while not duration.isdigit() or int(duration) <= 0:
        print("Error: Duration must be a positive number.")
        duration = input("Enter video duration (in minutes): ").strip()

    return topic, country, int(duration)


def create_content_brief(topic, country, duration):
    return {
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


def save_content(topic, country, duration):
    connection = sqlite3.connect("content_studio.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO content (topic, target_audience, duration)
        VALUES (?, ?, ?)
    """, (topic, country, duration))

    connection.commit()
    connection.close()

    print("\nContent saved successfully!")


def get_saved_content():
    connection = sqlite3.connect("content_studio.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, topic, target_audience, duration
        FROM content
        ORDER BY id DESC
    """)

    contents = cursor.fetchall()

    connection.close()

    return contents


def display_saved_content(contents):
    print("\n" + "=" * 50)
    print("           SAVED CONTENT")
    print("=" * 50)

    if not contents:
        print("\nNo content found.")
        return

    for content in contents:
        content_id, topic, country, duration = content

        print(f"\nID: {content_id}")
        print(f"Topic: {topic}")
        print(f"Target Audience: {country}")
        print(f"Duration: {duration} minutes")
        print("-" * 50)


def update_content():
    contents = get_saved_content()

    display_saved_content(contents)

    if not contents:
        return

    content_id = input("\nEnter the ID you want to update: ").strip()

    if not content_id.isdigit():
        print("Invalid ID.")
        return

    new_topic = input("Enter new topic: ").strip()
    new_country = input("Enter new target country: ").strip()
    new_duration = input("Enter new duration: ").strip()

    if not new_topic or not new_country:
        print("Topic and country cannot be empty.")
        return

    if not new_duration.isdigit() or int(new_duration) <= 0:
        print("Duration must be a positive number.")
        return

    connection = sqlite3.connect("content_studio.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE content
        SET topic = ?, target_audience = ?, duration = ?
        WHERE id = ?
    """, (new_topic, new_country, int(new_duration), int(content_id)))

    if cursor.rowcount == 0:
        print("\nContent ID not found.")
    else:
        print("\nContent updated successfully!")

    connection.commit()
    connection.close()


def delete_content():
    contents = get_saved_content()

    display_saved_content(contents)

    if not contents:
        return

    content_id = input("\nEnter the ID you want to delete: ").strip()

    if not content_id.isdigit():
        print("Invalid ID.")
        return

    connection = sqlite3.connect("content_studio.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM content
        WHERE id = ?
    """, (int(content_id),))

    if cursor.rowcount == 0:
        print("\nContent ID not found.")
    else:
        print("\nContent deleted successfully!")

    connection.commit()
    connection.close()


def main():
    while True:
        print("\n" + "=" * 50)
        print("              MAIN MENU")
        print("=" * 50)

        print("\n1. Create Content")
        print("2. View Saved Content")
        print("3. Update Content")
        print("4. Delete Content")
        print("5. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            topic, country, duration = get_video_details()

            brief = create_content_brief(
                topic,
                country,
                duration
            )

            print("\nContent Brief Created!")
            print("Topic:", brief["topic"])
            print("Target Audience:", brief["target_audience"])
            print("Duration:", brief["duration"], "minutes")

            save_content(topic, country, duration)

        elif choice == "2":
            contents = get_saved_content()
            display_saved_content(contents)

        elif choice == "3":
            update_content()

        elif choice == "4":
            delete_content()

        elif choice == "5":
            print("\nAI Content Studio closed.")
            break

        else:
            print("\nInvalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()