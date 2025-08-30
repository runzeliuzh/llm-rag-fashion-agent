import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faBrain, 
  faSearch, 
  faTshirt, 
  faCode,
  faRocket,
  faLightbulb,
  faMagic,
  faChartBar
} from '@fortawesome/free-solid-svg-icons';

const Features = () => {
  const features = [
    {
      icon: faBrain,
      title: "RAG Implementation",
      description: "Demonstrates Retrieval-Augmented Generation with ChromaDB vector store and semantic search for contextually relevant responses.",
      tech: "ChromaDB + DeepSeek API"
    },
    {
      icon: faSearch,
      title: "Vector Search System",
      description: "Implements semantic similarity search using embeddings to retrieve relevant fashion content before generation.",
      tech: "Text Embeddings + Cosine Similarity"
    },
    {
      icon: faTshirt,
      title: "Domain-Specific AI",
      description: "Showcases how RAG can be applied to specific domains like fashion advice and styling recommendations.",
      tech: "Domain-focused prompting + Retrieved context"
    },
    {
      icon: faCode,
      title: "Full-Stack Development",
      description: "Complete application demonstrating modern web development with API design, state management, and responsive UI.",
      tech: "React + FastAPI + Python"
    },
    {
      icon: faRocket,
      title: "Rate Limiting & UX",
      description: "Client-server rate limiting system with graceful degradation and offline handling for production-ready user experience.",
      tech: "Anonymous rate limiting + Error handling"
    },
    {
      icon: faLightbulb,
      title: "Deployment Ready",
      description: "Configured for cost-effective cloud deployment with environment management and containerization.",
      tech: "Docker + Environment Config + CORS"
    }
  ];

  const techStack = [
    { category: "Frontend", items: ["React 18", "Tailwind CSS", "Modern Hooks", "Responsive Design"] },
    { category: "Backend", items: ["FastAPI", "Python 3.9+", "Async/Await", "API Design"] },
    { category: "AI/RAG", items: ["ChromaDB", "Vector Embeddings", "DeepSeek LLM", "Semantic Search"] },
    { category: "DevOps", items: ["Docker", "Environment Config", "Rate Limiting", "CORS"] }
  ];

  const howItWorks = [
    {
      step: "1",
      title: "Question Processing",
      description: "User query is received and prepared for vector search"
    },
    {
      step: "2", 
      title: "Vector Retrieval",
      description: "ChromaDB searches 12 fashion articles using semantic similarity to find relevant context"
    },
    {
      step: "3",
      title: "Context Augmentation",
      description: "Retrieved articles are combined with user query to create enriched prompt for LLM"
    },
    {
      step: "4",
      title: "AI Response",
      description: "DeepSeek LLM generates contextually aware fashion advice based on retrieved knowledge"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            RAG Fashion Assistant Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-4xl mx-auto">
            A demo project demonstrating Retrieval-Augmented Generation (RAG) implementation 
            for domain-specific AI applications.  
          </p>
      
        </div>

        {/* How It Works */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-8">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {howItWorks.map((step, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {step.step}
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">{step.title}</h3>
                <p className="text-sm text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-8">Key Features & Technical Decisions</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center mb-4">
                  <FontAwesomeIcon icon={feature.icon} className="text-2xl text-purple-600 mr-3" />
                  <h3 className="text-lg font-semibold text-gray-800">{feature.title}</h3>
                </div>
                <p className="text-gray-600 mb-3">{feature.description}</p>
                <div className="mb-3">
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                    {feature.tech}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-8">Technology Stack</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {techStack.map((category, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
                  <FontAwesomeIcon icon={faCode} className="text-purple-600 mr-2" />
                  {category.category}
                </h3>
                <ul className="space-y-2">
                  {category.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="text-gray-600 text-sm">• {item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Project Stats */}
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Project Overview</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <FontAwesomeIcon icon={faChartBar} className="text-3xl text-purple-600 mb-2" />
              <h3 className="text-xl font-semibold text-gray-800">Architecture</h3>
              <p className="text-gray-600">Full-stack RAG application with vector search and LLM integration</p>
            </div>
            <div>
              <FontAwesomeIcon icon={faMagic} className="text-3xl text-purple-600 mb-2" />
              <h3 className="text-xl font-semibold text-gray-800">Implementation</h3>
              <p className="text-gray-600">Clean, production-ready code with modern development practices</p>
            </div>
            <div>
              <FontAwesomeIcon icon={faRocket} className="text-3xl text-purple-600 mb-2" />
              <h3 className="text-xl font-semibold text-gray-800">Deployment</h3>
              <p className="text-gray-600">Containerized application ready for cloud deployment</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            This project demonstrates practical application of AI technologies in a real-world scenario.
          </p>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Try the Application
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
