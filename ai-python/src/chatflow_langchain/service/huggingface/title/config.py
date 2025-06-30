class OPENAIMODEL:
      GPT_35='gpt-3.5-turbo'
      GPT_4o_MINI ='gpt-4.1-mini'
class REFORMED_QUERY:
      QUERY_LIMIT_CHECK=3000
      REFORMED_QUERY_LIMIT=3000
class QUOTES:
      UNWANTED_QUOTES =["'''", '"""', '"', "'", '`','’', '‘','“','‘']

class DEFAULT_HUGGINGFACE_TITLES:
    TITLES = {
      "ValueError": [
            "Unexpected Value Provided",
            "Input Value Requires Adjustment",
            "Check Input Format and Value"
      ],
      "RuntimeError": [
            "Processing Interrupted",
            "Processing issue detected",
            "Execution Stopped Mid-Process",
            "Operation failed unexpectedly",
            "Unexpected System Halt"
      ],
      "EntryNotFoundError": [
            "Entry Not Located"
            "Requested Information Unavailable",
            "Requested Entry Missing"
      ],
      "BadRequestError": [
            "Request Format Needs Attention",
            "Format Needs Review",
            "Invalid Request Structure",
            "Invalid request setup"
      ],
      "HfHubHTTPError": [
            "Issue Accessing HF Hub",
            "Connection to HF Hub Unsuccessful",
            "HF Hub Response Unavailable"
      ],
      "HTTPError": [
            "Network Request Issue",
            "Communication Unsuccessful",
            "Request Not Completed"
      ],
      "default": [
            "Oops! There's a Glitch",
            "Whoops! Something's Off",
            "Oops! We Need a Moment",
            "Wait Up! Just a Moment",
            "Oops! Technical Hiccup",
            "Oops! We're on the Case"
      ]
    }




class DEFAULT_HUGGINGFACE_IMAGE_TITLES:
    TITLES =[
            "Visualizing Creativity",
            "From Words to Art",
            "Image Ideas in the Making",
            "Picture Perfect Conversations",
            "Transforming Thoughts into Images",
            "When Words Become Art",
            "Art from AI: Creating the Future",
            "Bringing Imagination to Life",
            "Vision in Action",
            "Unlocking the Visuals of Imagination",
            "Artistic Interpretation in Progress",
            "Creating Visual Masterpieces",
            "A Picture Speaks a Thousand Words",
            "The Art of Conversation",
            "The Visual Story Unfolds",
            "Interactive Image Creation",
            "Turning Words into Visual Wonders",
            "Sculpting Images from Dialogue",
            "From Ideas to Visuals",
            "The Image You Asked For",
            "Visual Inspirations in Motion",
            "The Canvas of the Mind",
            "Where AI Meets Art",
            "Designing Dreams",
            "Exploring Visual Possibilities",
            "The Magic of Image Generation",
            "Coloring Conversations",
            "Unveiling New Visual Worlds",
            "Crafting Images, One Chat at a Time",
            "Generative Art in Action",
            "Beyond Words: The Art of Creation",
            "A Journey into Visual Creation",
            "Creating Worlds with AI",
            "The Power of Visual Storytelling",
            "Sculpting New Realities",
            "Art Through AI: A New Perspective",
            "Pixels of Imagination",
            "Shaping Ideas into Art",
            "Seeing the Future Through Images",
            "Exploring Imaginary Landscapes",
            "Painting with AI Brushes",
            "Minds and Machines Creating Art",
            "Where Conversations Turn into Pictures",
            "The Intersection of Text and Visuals",
            "Digital Brushstrokes in Progress",
            "Visuals Born from Dialogue",
            "Picture This: A New Creation",
            "Seeing What We Speak",
            "AI Dreams, Real Images",
            "Imagining the Unseen",
            "Pixels in Motion",
            "The Digital Canvas Awakens",
            "Unleashing the Power of Imagination",
            "The Art of AI Vision",
            "Sketching the Future of AI",
            "Framing the Unknown",
            "Creating Beyond Boundaries",
            "Painting the Invisible",
            "Inspiring Digital Imagery",
            "Envisioning Tomorrow's Art",
            "The Future of Visuals is Here",
            "Seeing the World Through AI",
            "Bringing Dreams to Life",
            "The Image Within the Words",
            "AI-Driven Inspiration",
            "Visualizing Possibilities",
            "Unlocking the Potential of Pixels",
            "Imagining New Realities",
            "The Vision Behind the Creation",
            "Crafting Beauty from Code",
            "Exploring Digital Landscapes",
            "The Art of Algorithmic Imagination",
            "Where Ideas Blossom into Art",
            "From Code to Canvas",
            "AI: A New Kind of Artist",
            "Art in the Age of AI",
            "The Intersection of Thought and Image",
            "Discovering Worlds Through AI"
            ]