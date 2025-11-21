"""
Example: AI-Powered Content Generation
Using EchoFree for creative content generation
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

# from echo_engines.echo_free import EchoFreeEngine


class ContentGenerator:
    """AI-powered content generation system"""

    def __init__(self):
        # self.engine = EchoFreeEngine()
        pass

    async def generate_blog_post(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate a complete blog post"""

        print(f"Generating blog post about: {topic}")

        # Generate title ideas
        # title_ideas = await self.engine.brainstorm(
        #     f"Blog post titles about {topic}",
        #     num_ideas=5
        # )

        title_ideas = [
            f"The Ultimate Guide to {topic}",
            f"10 Things You Should Know About {topic}",
            f"How {topic} is Changing the Industry",
            f"A Deep Dive into {topic}",
            f"The Future of {topic}"
        ]

        selected_title = title_ideas[0]

        # Generate outline
        # outline = await self.engine.generate(
        #     f"Create detailed outline for blog post titled: {selected_title}"
        # )

        outline = f"""
        1. Introduction to {topic}
        2. Key Benefits
        3. Best Practices
        4. Real-World Examples
        5. Common Challenges
        6. Future Trends
        7. Conclusion
        """

        # Generate full content
        # content = await self.engine.generate(
        #     f"Write comprehensive blog post with title '{selected_title}' "
        #     f"following this outline: {outline}. "
        #     f"Include keywords: {', '.join(keywords)}"
        # )

        content = f"""
        # {selected_title}

        ## Introduction
        [Generated introduction about {topic}]

        ## Key Points
        [Detailed content incorporating keywords: {', '.join(keywords)}]

        ## Conclusion
        [Thoughtful conclusion]
        """

        # Generate meta description
        # meta_description = await self.engine.generate(
        #     f"Write SEO meta description for blog post: {selected_title}",
        #     parameters={"max_length": 160}
        # )

        meta_description = f"Comprehensive guide to {topic}. Learn best practices, trends, and more."

        return {
            "title": selected_title,
            "title_alternatives": title_ideas[1:],
            "outline": outline,
            "content": content,
            "meta_description": meta_description,
            "keywords": keywords,
            "word_count": len(content.split()),
            "generated_at": datetime.now().isoformat()
        }

    async def generate_social_media_content(self, topic: str, platforms: List[str]) -> Dict[str, List[str]]:
        """Generate social media posts for multiple platforms"""

        print(f"Generating social media content for: {', '.join(platforms)}")

        results = {}

        for platform in platforms:
            # Generate platform-specific posts
            # posts = await self.engine.generate(
            #     f"Create 5 engaging {platform} posts about {topic}. "
            #     f"Follow {platform} best practices for length and style."
            # )

            if platform == "twitter":
                posts = [
                    f"🚀 Exciting developments in {topic}! Here's what you need to know... #Tech",
                    f"Did you know? {topic} is revolutionizing the industry. Thread 🧵",
                    f"Quick tip: {topic} best practices you should implement today 💡",
                    f"The future of {topic} is here, and it's incredible! Learn more:",
                    f"Hot take: {topic} will change everything. Here's why... 🔥"
                ]
            elif platform == "linkedin":
                posts = [
                    f"Insights on {topic} and its impact on business operations.",
                    f"How {topic} is transforming our industry - key takeaways.",
                    f"Lessons learned from implementing {topic} in enterprise.",
                    f"The ROI of {topic}: What the data tells us.",
                    f"Future trends in {topic} - what to watch in 2025."
                ]
            elif platform == "instagram":
                posts = [
                    f"✨ {topic} inspiration ✨\n\n[Engaging caption]",
                    f"Behind the scenes: {topic} 📸",
                    f"Transform your workflow with {topic} 🚀",
                    f"Weekend vibes ✌️ Learning about {topic}",
                    f"Monday motivation: {topic} edition 💪"
                ]
            else:
                posts = [f"Generic post about {topic}" for _ in range(5)]

            results[platform] = posts

        return results

    async def generate_email_campaign(self, product: str, audience: str) -> Dict[str, Any]:
        """Generate email marketing campaign"""

        print(f"Generating email campaign for {product} targeting {audience}")

        # Generate subject lines
        # subject_lines = await self.engine.brainstorm(
        #     f"Email subject lines for {product} campaign targeting {audience}",
        #     num_ideas=10
        # )

        subject_lines = [
            f"Introducing {product} - Transform Your Workflow",
            f"You're Invited: Exclusive {product} Early Access",
            f"Last Chance: {product} Launch Special",
            f"See How {product} Can Help You",
            f"Don't Miss Out on {product}"
        ]

        # Generate email body
        # email_body = await self.engine.generate(
        #     f"Write compelling email for {product} targeting {audience}. "
        #     f"Include benefits, social proof, and clear CTA."
        # )

        email_body = f"""
        Hi there,

        We're excited to introduce {product} - designed specifically for {audience}.

        **Why {product}?**
        • Save time and increase productivity
        • Proven results from companies like yours
        • Easy to implement and use

        Join thousands of satisfied customers who have already transformed their workflow.

        [CTA Button: Get Started Today]

        Best regards,
        The Team
        """

        # Generate follow-up sequence
        # follow_ups = await self.engine.generate(
        #     f"Create 3-email follow-up sequence for {product} campaign"
        # )

        follow_ups = [
            {
                "day": 3,
                "subject": f"Quick question about {product}",
                "preview": "Just following up on our previous email..."
            },
            {
                "day": 7,
                "subject": f"Case study: How {audience} use {product}",
                "preview": "See real results from companies like yours..."
            },
            {
                "day": 14,
                "subject": f"Last chance: Special offer for {product}",
                "preview": "This exclusive offer expires soon..."
            }
        ]

        return {
            "subject_lines": subject_lines,
            "recommended_subject": subject_lines[0],
            "body": email_body,
            "follow_up_sequence": follow_ups,
            "target_audience": audience,
            "product": product
        }


# Example usage
async def main():
    generator = ContentGenerator()

    print("=" * 60)
    print("Echo Content Generation Examples")
    print("=" * 60)

    # Example 1: Blog Post
    print("\n1. Generating Blog Post...")
    blog_post = await generator.generate_blog_post(
        topic="Artificial Intelligence in Business",
        keywords=["AI", "automation", "productivity", "innovation"]
    )
    print(f"✓ Title: {blog_post['title']}")
    print(f"✓ Word Count: {blog_post['word_count']}")
    print(f"✓ Meta: {blog_post['meta_description']}")

    # Example 2: Social Media
    print("\n2. Generating Social Media Content...")
    social_content = await generator.generate_social_media_content(
        topic="Sustainable Technology",
        platforms=["twitter", "linkedin", "instagram"]
    )
    print(f"✓ Generated {sum(len(posts) for posts in social_content.values())} posts")
    print(f"✓ Platforms: {', '.join(social_content.keys())}")

    # Example 3: Email Campaign
    print("\n3. Generating Email Campaign...")
    email_campaign = await generator.generate_email_campaign(
        product="Echo AI Platform",
        audience="Small Business Owners"
    )
    print(f"✓ Subject: {email_campaign['recommended_subject']}")
    print(f"✓ Follow-ups: {len(email_campaign['follow_up_sequence'])}")

    print("\n" + "=" * 60)
    print("Content generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
