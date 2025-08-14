import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, RefreshCw, MessageSquare, Brain, Shield, AlertTriangle } from 'lucide-react';
import axios from 'axios';

// Configuration API
const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

const AssistantPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [assistantStatus, setAssistantStatus] = useState(null);
  const [context, setContext] = useState('');
  const messagesEndRef = useRef(null);

  // Contexts prédéfinis cybersécurité
  const predefinedContexts = [
    { value: '', label: 'Général' },
    { value: 'pentest', label: 'Tests de Pénétration' },
    { value: 'audit', label: 'Audit de Sécurité' },
    { value: 'incident', label: 'Réponse aux Incidents' },
    { value: 'forensique', label: 'Forensique Numérique' },
    { value: 'conformité', label: 'Conformité & Standards' },
    { value: 'owasp', label: 'OWASP & Web Security' },
    { value: 'cloud', label: 'Sécurité Cloud' },
    { value: 'mobile', label: 'Sécurité Mobile' }
  ];

  // Messages de démarrage suggestifs
  const startingPrompts = [
    "Comment réaliser un audit de sécurité complet ?",
    "Quelles sont les étapes d'un pentest web OWASP ?",
    "Comment investiguer un incident de sécurité ?",
    "Quels outils pour un audit de conformité GDPR ?",
    "Comment sécuriser une architecture cloud ?",
    "Que faire en cas de compromission détectée ?"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeAssistant();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const initializeAssistant = async () => {
    try {
      // Récupérer le status de l'assistant
      const statusResponse = await api.get('/api/assistant/status');
      setAssistantStatus(statusResponse.data);

      // Créer une nouvelle session
      const sessionResponse = await api.post('/api/assistant/sessions/new');
      setSessionId(sessionResponse.data.session_id);

      // Message de bienvenue
      setMessages([{
        role: 'assistant',
        content: `🛡️ **Bienvenue dans l'Assistant IA CyberSec Toolkit Pro 2025 !**

Je suis votre expert cybersécurité dédié, spécialisé dans l'ensemble des 35 services intégrés du toolkit portable.

**🎯 Je peux vous accompagner sur :**
- Tests de pénétration complets (web, réseau, mobile, IoT)
- Audits de sécurité et conformité (NIST, ISO 27001, GDPR)
- Réponse aux incidents et forensique numérique
- Architecture sécurisée et threat modeling
- Évaluation des risques et gouvernance

**💡 Tip :** Sélectionnez un contexte spécifique ci-dessus pour des réponses plus ciblées !

Comment puis-je vous aider aujourd'hui ?`,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Erreur initialisation assistant:', error);
      setMessages([{
        role: 'assistant',
        content: '⚠️ Assistant temporairement indisponible. Veuillez réessayer dans quelques instants.',
        timestamp: new Date()
      }]);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await api.post('/api/assistant/chat', {
        message: userMessage.content,
        session_id: sessionId,
        context: context || null
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        tokens_used: response.data.tokens_used,
        model_used: response.data.model_used
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Erreur envoi message:', error);
      const errorMessage = {
        role: 'assistant',
        content: '❌ Erreur lors de la communication avec l\'assistant. Veuillez réessayer.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const useStartingPrompt = (prompt) => {
    setInputMessage(prompt);
  };

  const clearConversation = () => {
    setMessages([]);
    initializeAssistant();
  };

  const formatMessage = (content) => {
    // Formater le markdown basique pour l'affichage
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/```(.*?)```/gs, '<pre class="bg-gray-100 p-2 rounded text-sm"><code>$1</code></pre>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Assistant IA Cybersécurité</h1>
              <p className="text-sm text-gray-500">
                {assistantStatus?.llm_configured ? 
                  `${assistantStatus.llm_provider} • ${assistantStatus.llm_model}` : 
                  'Mode Expert Intégré'
                }
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Sélecteur de contexte */}
            <select 
              value={context} 
              onChange={(e) => setContext(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {predefinedContexts.map(ctx => (
                <option key={ctx.value} value={ctx.value}>{ctx.label}</option>
              ))}
            </select>
            
            <button
              onClick={clearConversation}
              className="flex items-center space-x-1 px-3 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">Nouveau</span>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Démarrez une conversation</h3>
            <p className="text-gray-500 mb-6">Choisissez une question ou tapez la vôtre</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl mx-auto">
              {startingPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => useStartingPrompt(prompt)}
                  className="p-3 text-left border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start space-x-2">
                    <Shield className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{prompt}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex space-x-3 max-w-4xl ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.role === 'user' 
                  ? 'bg-blue-500' 
                  : 'bg-gray-200'
              }`}>
                {message.role === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-gray-600" />
                )}
              </div>
              
              <div className={`flex-1 ${message.role === 'user' ? 'text-right' : ''}`}>
                <div className={`inline-block p-4 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}>
                  <div 
                    className="text-sm leading-relaxed"
                    dangerouslySetInnerHTML={{ 
                      __html: formatMessage(message.content) 
                    }}
                  />
                </div>
                
                <div className={`mt-1 text-xs text-gray-500 ${message.role === 'user' ? 'text-right' : ''}`}>
                  {message.timestamp?.toLocaleTimeString()}
                  {message.model_used && ` • ${message.model_used}`}
                  {message.tokens_used && ` • ${message.tokens_used} tokens`}
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex space-x-3 max-w-4xl">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="flex-1">
                <div className="inline-block p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <span className="text-sm text-gray-600">L'assistant analyse votre demande...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Posez votre question cybersécurité${context ? ` sur ${predefinedContexts.find(c => c.value === context)?.label}` : ''}...`}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="2"
              disabled={isLoading}
            />
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="flex items-center justify-center w-12 h-12 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {assistantStatus && (
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${assistantStatus.status === 'operational' ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span>Assistant {assistantStatus.status === 'operational' ? 'opérationnel' : 'indisponible'}</span>
              {context && <span>• Contexte: {predefinedContexts.find(c => c.value === context)?.label}</span>}
            </div>
            <div>
              {assistantStatus.llm_configured ? 'LLM connecté' : 'Mode expert intégré'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssistantPage;