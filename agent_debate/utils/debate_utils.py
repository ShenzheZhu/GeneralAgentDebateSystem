from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class DebateUtils:
    """Debate utility class"""
    
    @staticmethod
    def save_debate_record(
        debate_id: str,
        topic: str,
        mode: str,
        messages: List[Dict[str, Any]],
        scores: Dict[str, float],
        summary: Dict[str, Any],
        output_dir: str = "debate_records"
    ) -> str:
        """
        Save debate record
        :param debate_id: Debate ID
        :param topic: Debate topic
        :param mode: Debate mode
        :param messages: Message list
        :param scores: Scores
        :param summary: Summary information
        :param output_dir: Output directory
        :return: Saved file path
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Build record data
        record = {
            "debate_id": debate_id,
            "topic": topic,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "scores": scores,
            "summary": summary
        }
        
        # Generate filename
        filename = f"{debate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            
        return filepath
        
    @staticmethod
    def load_debate_record(filepath: str) -> Dict[str, Any]:
        """
        Load debate record
        :param filepath: File path
        :return: Record data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @staticmethod
    def analyze_debate_quality(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze debate quality
        :param messages: Message list
        :return: Analysis results
        """
        analysis = {
            "total_messages": len(messages),
            "messages_per_agent": {},
            "average_message_length": 0,
            "topic_consistency": 0.0,
            "interaction_depth": 0.0
        }
        
        if not messages:
            return analysis
            
        # Calculate the number of messages per agent
        for msg in messages:
            sender = msg["sender"]
            if sender not in analysis["messages_per_agent"]:
                analysis["messages_per_agent"][sender] = 0
            analysis["messages_per_agent"][sender] += 1
            
        # Calculate the average message length
        total_length = sum(len(msg["content"]) for msg in messages)
        analysis["average_message_length"] = total_length / len(messages)
        
        # Calculate topic consistency (simple implementation)
        topic_words = set(messages[0].get("topic", "").lower().split())
        topic_mentions = sum(
            1 for msg in messages
            if any(word in msg["content"].lower() for word in topic_words)
        )
        analysis["topic_consistency"] = topic_mentions / len(messages)
        
        # Calculate interaction depth (reply relationship)
        replies = sum(1 for msg in messages if msg.get("reply_to"))
        analysis["interaction_depth"] = replies / len(messages)
        
        return analysis
        
    @staticmethod
    def extract_key_points(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract key points
        :param messages: Message list
        :return: Key points list
        """
        key_points = []
        
        for msg in messages:
            # Extract sentences containing keywords
            content = msg["content"]
            sentences = content.split(". ")
            
            key_sentences = []
            keywords = ["because", "therefore", "however", "moreover", "conclude"]
            
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    key_sentences.append(sentence)
                    
            if key_sentences:
                key_points.append({
                    "round": msg.get("round_number"),
                    "agent": msg["sender"],
                    "points": key_sentences
                })
                
        return key_points
        
    @staticmethod
    def calculate_engagement_metrics(
        messages: List[Dict[str, Any]],
        time_window: int = 300  # 5分钟
    ) -> Dict[str, float]:
        """
        Calculate engagement metrics
        :param messages: Message list
        :param time_window: Time window (seconds)
        :return: Engagement metrics
        """
        if not messages:
            return {
                "message_frequency": 0.0,
                "response_rate": 0.0,
                "engagement_score": 0.0
            }
            
        # Calculate message frequency
        start_time = datetime.fromisoformat(messages[0]["timestamp"])
        end_time = datetime.fromisoformat(messages[-1]["timestamp"])
        duration = (end_time - start_time).total_seconds()
        message_frequency = len(messages) / (duration / time_window)
        
        # Calculate response rate
        total_replies = sum(1 for msg in messages if msg.get("reply_to"))
        response_rate = total_replies / len(messages)
        
        # Calculate comprehensive engagement score
        engagement_score = (message_frequency * 0.4 + response_rate * 0.6)
        
        return {
            "message_frequency": message_frequency,
            "response_rate": response_rate,
            "engagement_score": engagement_score
        }
        
    @staticmethod
    def generate_debate_statistics(
        messages: List[Dict[str, Any]],
        scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate debate statistics
        :param messages: Message list
        :param scores: Scores
        :return: Statistics
        """
        stats = {
            "duration": {
                "total_seconds": 0,
                "average_round_time": 0
            },
            "participation": {
                "total_participants": len(set(msg["sender"] for msg in messages)),
                "messages_per_participant": {}
            },
            "scores": {
                "highest_score": max(scores.values()) if scores else 0,
                "average_score": sum(scores.values()) / len(scores) if scores else 0,
                "score_distribution": scores
            },
            "content": {
                "total_messages": len(messages),
                "average_length": 0,
                "rounds": len(set(msg.get("round_number", 0) for msg in messages))
            }
        }
        
        # Calculate time-related statistics
        if messages:
            start_time = datetime.fromisoformat(messages[0]["timestamp"])
            end_time = datetime.fromisoformat(messages[-1]["timestamp"])
            total_seconds = (end_time - start_time).total_seconds()
            stats["duration"]["total_seconds"] = total_seconds
            stats["duration"]["average_round_time"] = total_seconds / stats["content"]["rounds"]
            
        # Calculate participation statistics
        for msg in messages:
            sender = msg["sender"]
            if sender not in stats["participation"]["messages_per_participant"]:
                stats["participation"]["messages_per_participant"][sender] = 0
            stats["participation"]["messages_per_participant"][sender] += 1
            
        # Calculate content statistics
        total_length = sum(len(msg["content"]) for msg in messages)
        stats["content"]["average_length"] = total_length / len(messages) if messages else 0
        
        return stats 