import pandas as pd
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ast
from typing import List, Dict, Any, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score

class InterestCompetenceGraphRecommender:
    """
    A novel recommendation system that builds a knowledge graph from student data,
    combining social network analysis, competence mapping, and interest similarity
    to provide personalized recommendations for potential collaborators.
    """
    
    def __init__(self, data_path: str):
        """Initialize the recommender with the dataset path."""
        self.data_path = data_path
        self.df = None
        self.graph = nx.Graph()
        self.interest_matrix = None
        self.competence_matrix = None
        self.community_matrix = None
        self.embeddings = {}
        self.evaluation_metrics = {}
        
    def load_data(self) -> None:
        """Load and preprocess the dataset."""
        self.df = pd.read_csv(self.data_path)
        
        # Convert string representations of lists to actual lists
        for col in ['Coéquipiers', 'Communautés', 'Compétences', "Centres_d'Intérêt"]:
            self.df[col] = self.df[col].apply(ast.literal_eval)
        
        print(f"Loaded data with {len(self.df)} students")
    
    def build_graph(self) -> None:
        """Build the knowledge graph representing student relationships."""
        # Add nodes for each student
        for idx, row in self.df.iterrows():
            student_id = row['ID_Étudiant']
            self.graph.add_node(
                student_id, 
                name=row['Nom'],
                collab_score=row['Travaux_Collaboratifs'],
                interactions=row['Nombre_Interactions'],
                communities=row['Communautés'],
                skills=row['Compétences'],
                interests=row["Centres_d'Intérêt"]
            )
        
        # Add edges for collaborations
        for idx, row in self.df.iterrows():
            student_id = row['ID_Étudiant']
            for teammate_id in row['Coéquipiers']:
                if teammate_id in self.df['ID_Étudiant'].values:
                    # Weight edges by the average of the two students' collaborative work scores
                    teammate_row = self.df[self.df['ID_Étudiant'] == teammate_id].iloc[0]
                    weight = (row['Travaux_Collaboratifs'] + teammate_row['Travaux_Collaboratifs']) / 2
                    self.graph.add_edge(student_id, teammate_id, weight=weight)
        
        # Add community-based edges
        for idx, row in self.df.iterrows():
            student_id = row['ID_Étudiant']
            for other_idx, other_row in self.df.iterrows():
                if student_id != other_row['ID_Étudiant']:
                    # Calculate community overlap
                    common_communities = set(row['Communautés']).intersection(set(other_row['Communautés']))
                    if common_communities:
                        weight = len(common_communities) * 0.5  # Adjust weight for community connections
                        if self.graph.has_edge(student_id, other_row['ID_Étudiant']):
                            # Add to existing edge weight
                            self.graph[student_id][other_row['ID_Étudiant']]['weight'] += weight
                        else:
                            self.graph.add_edge(student_id, other_row['ID_Étudiant'], weight=weight)
        
        # Print graph metrics
        print(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        print(f"Graph density: {nx.density(self.graph):.4f}")
        print(f"Average clustering coefficient: {nx.average_clustering(self.graph):.4f}")
        
        # Calculate and store connected components
        connected_components = list(nx.connected_components(self.graph))
        print(f"Number of connected components: {len(connected_components)}")
        print(f"Size of largest component: {len(max(connected_components, key=len))}")
    
    def create_feature_matrices(self) -> None:
        """Create matrices for interests, competencies and communities."""
        # Get all unique interests, competencies, and communities
        all_interests = set()
        all_competencies = set()
        all_communities = set()
        
        for _, row in self.df.iterrows():
            all_interests.update(row["Centres_d'Intérêt"])
            all_competencies.update(row['Compétences'])
            all_communities.update(row['Communautés'])
        
        # Create binary matrices
        interest_matrix = np.zeros((len(self.df), len(all_interests)))
        competence_matrix = np.zeros((len(self.df), len(all_competencies)))
        community_matrix = np.zeros((len(self.df), len(all_communities)))
        
        interest_map = {interest: i for i, interest in enumerate(all_interests)}
        competence_map = {comp: i for i, comp in enumerate(all_competencies)}
        community_map = {comm: i for i, comm in enumerate(all_communities)}
        
        for i, (_, row) in enumerate(self.df.iterrows()):
            for interest in row["Centres_d'Intérêt"]:
                interest_matrix[i, interest_map[interest]] = 1
                
            for competence in row['Compétences']:
                competence_matrix[i, competence_map[competence]] = 1
                
            for community in row['Communautés']:
                community_matrix[i, community_map[community]] = 1
        
        self.interest_matrix = interest_matrix
        self.competence_matrix = competence_matrix
        self.community_matrix = community_matrix
        self.interest_map = interest_map
        self.competence_map = competence_map
        self.community_map = community_map
        
        # Print feature matrix statistics
        print(f"\nFeature matrix statistics:")
        print(f"Interest matrix shape: {interest_matrix.shape}")
        print(f"Interest matrix density: {np.mean(interest_matrix):.4f}")
        print(f"Competence matrix shape: {competence_matrix.shape}")
        print(f"Competence matrix density: {np.mean(competence_matrix):.4f}")
        print(f"Community matrix shape: {community_matrix.shape}")
        print(f"Community matrix density: {np.mean(community_matrix):.4f}")
    
    def generate_embeddings(self) -> None:
        """
        Generate embeddings for each student combining graph structure,
        interests, competencies, and community membership.
        """
        # Calculate centrality measures
        print("\nCalculating network centrality measures...")
        centrality = nx.eigenvector_centrality_numpy(self.graph, weight='weight')
        clustering = nx.clustering(self.graph, weight='weight')
        
        # Print centrality statistics
        centrality_values = list(centrality.values())
        print(f"Centrality stats - Min: {min(centrality_values):.4f}, Max: {max(centrality_values):.4f}, Avg: {np.mean(centrality_values):.4f}")
        
        # Calculate similarities
        print("Calculating similarity matrices...")
        interest_sim = cosine_similarity(self.interest_matrix)
        competence_sim = cosine_similarity(self.competence_matrix)
        community_sim = cosine_similarity(self.community_matrix)
        
        # Print similarity statistics
        print(f"Interest similarity matrix - Avg: {np.mean(interest_sim):.4f}, Std: {np.std(interest_sim):.4f}")
        print(f"Competence similarity matrix - Avg: {np.mean(competence_sim):.4f}, Std: {np.std(competence_sim):.4f}")
        print(f"Community similarity matrix - Avg: {np.mean(community_sim):.4f}, Std: {np.std(community_sim):.4f}")
        
        # Generate embeddings for each student
        for i, student_id in enumerate(self.df['ID_Étudiant']):
            student_row = self.df[self.df['ID_Étudiant'] == student_id].iloc[0]
            
            # Combine features into an embedding
            embedding = {
                # Graph metrics
                'centrality': centrality.get(student_id, 0),
                'clustering': clustering.get(student_id, 0),
                
                # Node attributes
                'collab_score': student_row['Travaux_Collaboratifs'] / 10,  # Normalize
                'interactions': student_row['Nombre_Interactions'] / 100,  # Normalize
                
                # Similarity matrices
                'interest_sim': interest_sim[i],
                'competence_sim': competence_sim[i],
                'community_sim': community_sim[i]
            }
            
            self.embeddings[student_id] = embedding
        
        print(f"Generated embeddings for {len(self.embeddings)} students")
    
    def get_recommendations(self, student_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a student.
        
        Args:
            student_id: ID of the student to get recommendations for
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended students with similarity scores and reasons
        """
        if student_id not in self.df['ID_Étudiant'].values:
            raise ValueError(f"Student ID {student_id} not found in dataset")
            
        student_idx = self.df[self.df['ID_Étudiant'] == student_id].index[0]
        student_embedding = self.embeddings[student_id]
        
        recommendations = []
        
        for other_id in self.df['ID_Étudiant']:
            if other_id == student_id:
                continue
                
            other_idx = self.df[self.df['ID_Étudiant'] == other_id].index[0]
            other_embedding = self.embeddings[other_id]
            
            # Calculate similarity scores between the students
            similarity_scores = {
                'interest': 0.0,
                'competence': 0.0,
                'community': 0.0,
                'network': 0.0,
                'collab': 0.0
            }
            
            # Interest similarity (higher weight)
            interest_sim = np.dot(student_embedding['interest_sim'], other_embedding['interest_sim'])
            similarity_scores['interest'] = float(interest_sim * 0.35)
            
            # Competence complementarity (look for complementary skills)
            competence_sim = np.dot(student_embedding['competence_sim'], other_embedding['competence_sim'])
            similarity_scores['competence'] = float(competence_sim * 0.25)
            
            # Community overlap
            community_sim = np.dot(student_embedding['community_sim'], other_embedding['community_sim'])
            similarity_scores['community'] = float(community_sim * 0.2)
            
            # Network proximity (if they're close in the graph)
            if self.graph.has_edge(student_id, other_id):
                similarity_scores['network'] = float(self.graph[student_id][other_id]['weight'] * 0.1)
            else:
                try:
                    # Find shortest path if they're not directly connected
                    path_length = nx.shortest_path_length(self.graph, student_id, other_id)
                    similarity_scores['network'] = float(max(0, (5 - path_length) / 5) * 0.1)
                except nx.NetworkXNoPath:
                    similarity_scores['network'] = 0.0
            
            # Collaborative work score similarity
            collab_diff = abs(student_embedding['collab_score'] - other_embedding['collab_score'])
            similarity_scores['collab'] = float((1 - collab_diff) * 0.1)
            
            # Calculate overall similarity
            overall_similarity = float(sum(similarity_scores.values()))
            
            # Get explanation for recommendation
            reasons = self._generate_recommendation_reasons(student_id, other_id, similarity_scores)
            
            # Add to recommendations
            other_name = self.df.loc[other_idx, 'Nom']
            recommendations.append({
                'id': int(other_id),
                'name': other_name,
                'similarity': overall_similarity,
                'similarity_breakdown': similarity_scores,
                'reasons': reasons
            })
        
        # Sort by similarity and return top N
        recommendations.sort(key=lambda x: x['similarity'], reverse=True)
        return recommendations[:top_n]
    
    def _generate_recommendation_reasons(
        self, student_id: int, other_id: int, similarity_scores: Dict[str, float]
    ) -> List[str]:
        """Generate explanations for why a recommendation was made."""
        student = self.df[self.df['ID_Étudiant'] == student_id].iloc[0]
        other = self.df[self.df['ID_Étudiant'] == other_id].iloc[0]
        
        reasons = []
        
        # Check common interests
        common_interests = set(student["Centres_d'Intérêt"]).intersection(set(other["Centres_d'Intérêt"]))
        if common_interests:
            reasons.append(f"Intérêts communs: {', '.join(common_interests)}")
        
        # Check complementary skills
        unique_skills = set(other['Compétences']).difference(set(student['Compétences']))
        if unique_skills:
            reasons.append(f"Compétences complémentaires: {', '.join(unique_skills)}")
        
        # Check common communities
        common_communities = set(student['Communautés']).intersection(set(other['Communautés']))
        if common_communities:
            reasons.append(f"Communautés partagées: {', '.join(common_communities)}")
        
        # Check network connection
        if self.graph.has_edge(student_id, other_id):
            reasons.append("Connexion directe dans le réseau")
        elif similarity_scores.get('network', 0) > 0:
            reasons.append("Connexion indirecte dans le réseau")
        
        # Check collaboration style
        if abs(student['Travaux_Collaboratifs'] - other['Travaux_Collaboratifs']) <= 2:
            reasons.append("Style de collaboration similaire")
        
        return reasons
    
    def evaluate_recommendations(self, validation_data: List[Tuple[int, List[int]]]) -> Dict[str, float]:
        """
        Evaluate recommendation quality using known collaborations.
        
        Args:
            validation_data: List of (student_id, [known_collaborator_ids]) tuples
            
        Returns:
            Dictionary of evaluation metrics
        """
        print("\nEvaluating recommendation quality...")
        precisions = []
        recalls = []
        f1_scores = []
        hit_rates = []
        
        for student_id, true_collaborators in validation_data:
            # Get recommendations
            recommendations = self.get_recommendations(student_id, top_n=10)
            recommended_ids = [rec['id'] for rec in recommendations]
            
            # Calculate precision and recall
            true_positives = set(recommended_ids).intersection(set(true_collaborators))
            precision = len(true_positives) / len(recommended_ids) if recommended_ids else 0
            recall = len(true_positives) / len(true_collaborators) if true_collaborators else 0
            
            # Calculate F1 score
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            # Calculate hit rate (if at least one recommendation is correct)
            hit_rate = 1.0 if true_positives else 0.0
            
            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)
            hit_rates.append(hit_rate)
            
        # Calculate average metrics
        avg_precision = np.mean(precisions)
        avg_recall = np.mean(recalls)
        avg_f1 = np.mean(f1_scores)
        avg_hit_rate = np.mean(hit_rates)
        
        # Store and return metrics
        metrics = {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': avg_f1,
            'hit_rate': avg_hit_rate
        }
        
        self.evaluation_metrics = metrics
        
        print(f"Recommendation evaluation metrics:")
        print(f"  Precision: {avg_precision:.4f}")
        print(f"  Recall: {avg_recall:.4f}")
        print(f"  F1 Score: {avg_f1:.4f}")
        print(f"  Hit Rate: {avg_hit_rate:.4f}")
        
        return metrics
    
    def evaluate_with_cross_validation(self, k_folds: int = 5) -> Dict[str, float]:
        """
        Evaluate the recommender using k-fold cross-validation.
        
        Args:
            k_folds: Number of folds for cross-validation
            
        Returns:
            Dictionary of evaluation metrics averaged across folds
        """
        print(f"\nPerforming {k_folds}-fold cross-validation...")
        
        # Prepare data for cross-validation
        all_student_ids = self.df['ID_Étudiant'].values
        np.random.shuffle(all_student_ids)
        
        # Split into folds
        folds = np.array_split(all_student_ids, k_folds)
        
        all_metrics = []
        
        for i in range(k_folds):
            print(f"\nFold {i+1}/{k_folds}:")
            
            # Create validation data
            validation_students = folds[i]
            validation_data = []
            
            for student_id in validation_students:
                student_row = self.df[self.df['ID_Étudiant'] == student_id].iloc[0]
                known_collaborators = student_row['Coéquipiers']
                validation_data.append((student_id, known_collaborators))
            
            # Evaluate on this fold
            fold_metrics = self.evaluate_recommendations(validation_data)
            all_metrics.append(fold_metrics)
        
        # Average metrics across folds
        avg_metrics = {
            'precision': np.mean([m['precision'] for m in all_metrics]),
            'recall': np.mean([m['recall'] for m in all_metrics]),
            'f1_score': np.mean([m['f1_score'] for m in all_metrics]),
            'hit_rate': np.mean([m['hit_rate'] for m in all_metrics])
        }
        
        print("\nCross-validation average metrics:")
        print(f"  Precision: {avg_metrics['precision']:.4f}")
        print(f"  Recall: {avg_metrics['recall']:.4f}")
        print(f"  F1 Score: {avg_metrics['f1_score']:.4f}")
        print(f"  Hit Rate: {avg_metrics['hit_rate']:.4f}")
        
        return avg_metrics
    
    def analyze_feature_importance(self) -> Dict[str, float]:
        """
        Analyze the importance of different features in making recommendations.
        
        Returns:
            Dictionary mapping feature names to their importance scores
        """
        print("\nAnalyzing feature importance...")
        
        # We'll measure feature importance by calculating the correlation
        # between each feature's similarity and the overall recommendation score
        
        feature_importance = {}
        all_similarities = []
        all_overall_scores = []
        
        # Sample student pairs
        num_samples = min(500, len(self.df) * (len(self.df) - 1) // 2)  # Limit to 500 samples
        student_ids = self.df['ID_Étudiant'].values
        
        sample_pairs = []
        for i in range(len(student_ids)):
            for j in range(i+1, len(student_ids)):
                sample_pairs.append((student_ids[i], student_ids[j]))
        
        # Randomly sample if we have too many pairs
        if len(sample_pairs) > num_samples:
            np.random.shuffle(sample_pairs)
            sample_pairs = sample_pairs[:num_samples]
        
        # Calculate similarities for each pair
        for student_id1, student_id2 in sample_pairs:
            student_embedding1 = self.embeddings[student_id1]
            student_embedding2 = self.embeddings[student_id2]
            
            # Calculate feature similarities
            similarities = {}
            
            # Interest similarity
            interest_sim = np.dot(student_embedding1['interest_sim'], student_embedding2['interest_sim'])
            similarities['interest'] = interest_sim
            
            # Competence similarity
            competence_sim = np.dot(student_embedding1['competence_sim'], student_embedding2['competence_sim'])
            similarities['competence'] = competence_sim
            
            # Community similarity
            community_sim = np.dot(student_embedding1['community_sim'], student_embedding2['community_sim'])
            similarities['community'] = community_sim
            
            # Network proximity
            if self.graph.has_edge(student_id1, student_id2):
                similarities['network'] = self.graph[student_id1][student_id2]['weight']
            else:
                try:
                    path_length = nx.shortest_path_length(self.graph, student_id1, student_id2)
                    similarities['network'] = max(0, (5 - path_length) / 5)
                except nx.NetworkXNoPath:
                    similarities['network'] = 0
            
            # Collaboration style similarity
            collab_diff = abs(student_embedding1['collab_score'] - student_embedding2['collab_score'])
            similarities['collab'] = 1 - collab_diff
            
            # Calculate overall similarity (weighted sum)
            weights = {
                'interest': 0.35,
                'competence': 0.25,
                'community': 0.20,
                'network': 0.10,
                'collab': 0.10
            }
            
            overall_score = sum(similarities[f] * weights[f] for f in similarities)
            
            # Store data for correlation calculation
            for feature, score in similarities.items():
                if feature not in all_similarities:
                    all_similarities.append(feature)
                    all_overall_scores.append([])
                feature_idx = all_similarities.index(feature)
                all_overall_scores[feature_idx].append((score, overall_score))
        
        # Calculate correlations
        for i, feature in enumerate(all_similarities):
            feature_scores = np.array([s[0] for s in all_overall_scores[i]])
            overall_scores = np.array([s[1] for s in all_overall_scores[i]])
            
            if np.std(feature_scores) > 0 and np.std(overall_scores) > 0:
                correlation = np.corrcoef(feature_scores, overall_scores)[0, 1]
                feature_importance[feature] = correlation
            else:
                feature_importance[feature] = 0
        
        # Print feature importance
        print("Feature importance scores (correlation with overall recommendation score):")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {feature}: {importance:.4f}")
        
        return feature_importance
    
    def train(self) -> None:
        """Train the recommendation model."""
        print("Training recommender system...")
        self.load_data()
        self.build_graph()
        self.create_feature_matrices()
        self.generate_embeddings()
        print("\nRecommender system trained successfully!")
        
        # Run evaluation if we have actual collaboration data
        if 'Coéquipiers' in self.df.columns:
            print("\nRunning evaluation on existing collaborations...")
            validation_data = []
            for _, row in self.df.iterrows():
                student_id = row['ID_Étudiant']
                known_collaborators = row['Coéquipiers']
                if known_collaborators:  # Only include if there are known collaborators
                    validation_data.append((student_id, known_collaborators))
            
            if validation_data:
                self.evaluate_recommendations(validation_data)
                self.evaluate_with_cross_validation()
                self.analyze_feature_importance()
        
    def get_student_info(self, student_id: int) -> Dict[str, Any]:
        """Get information about a specific student."""
        if student_id not in self.df['ID_Étudiant'].values:
            raise ValueError(f"Student ID {student_id} not found in dataset")
            
        student = self.df[self.df['ID_Étudiant'] == student_id].iloc[0]
        
        return {
            'id': int(student_id),
            'name': student['Nom'],
            'collab_score': student['Travaux_Collaboratifs'],
            'interactions': student['Nombre_Interactions'],
            'communities': student['Communautés'],
            'skills': student['Compétences'],
            'interests': student["Centres_d'Intérêt"]
        }
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get information about all students."""
        students = []
        for _, student in self.df.iterrows():
            students.append({
                'id': int(student['ID_Étudiant']),
                'name': student['Nom']
            })
        return students
    
    def print_summary_statistics(self) -> None:
        """Print summary statistics about the recommendation system."""
        print("\n===== RECOMMENDER SYSTEM SUMMARY =====")
        print(f"Dataset: {self.data_path}")
        print(f"Number of students: {len(self.df)}")
        
        # Graph statistics
        print("\nGraph Statistics:")
        print(f"  Nodes: {self.graph.number_of_nodes()}")
        print(f"  Edges: {self.graph.number_of_edges()}")
        print(f"  Density: {nx.density(self.graph):.4f}")
        print(f"  Average clustering: {nx.average_clustering(self.graph):.4f}")
        print(f"  Average degree: {np.mean([d for _, d in self.graph.degree()]):.2f}")
        
        # Feature statistics
        if hasattr(self, 'interest_map'):
            print("\nFeature Statistics:")
            print(f"  Number of unique interests: {len(self.interest_map)}")
            print(f"  Number of unique competencies: {len(self.competence_map)}")
            print(f"  Number of unique communities: {len(self.community_map)}")
        
        # Evaluation metrics
        if self.evaluation_metrics:
            print("\nEvaluation Metrics:")
            for metric, value in self.evaluation_metrics.items():
                print(f"  {metric}: {value:.4f}")
        
        print("=====================================")

# Example usage
if __name__ == "__main__":
    recommender = InterestCompetenceGraphRecommender("Dataset/dataset_etudiants.csv")
    recommender.train()
    
    # Print summary statistics
    recommender.print_summary_statistics()
    
    # Get recommendations for student 1
    student_id = 1
    student_info = recommender.get_student_info(student_id)
    print(f"\nRecommendations for {student_info['name']} (ID: {student_id}):")
    
    recommendations = recommender.get_recommendations(student_id)
    print(f"Found {len(recommendations)} recommended collaborators:")
    
    for i, rec in enumerate(recommendations):
        print(f"\n{i+1}. {rec['name']} (Similarity: {rec['similarity']:.4f})")
        print(f"   Similarity breakdown:")
        for factor, score in rec['similarity_breakdown'].items():
            print(f"     - {factor}: {score:.4f}")
        print("   Reasons:")
        for reason in rec['reasons']:
            print(f"     * {reason}")
    
    print("\nAccuracy Analysis:")
    # Check if the recommendations match actual collaborators
    actual_collaborators = set(student_info.get('Coéquipiers', []))
    recommended_ids = {rec['id'] for rec in recommendations}
    true_positives = recommended_ids.intersection(actual_collaborators)
    
    if actual_collaborators:
        precision = len(true_positives) / len(recommended_ids) if recommended_ids else 0
        recall = len(true_positives) / len(actual_collaborators) if actual_collaborators else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        print(f"  Correctly recommended: {len(true_positives)} out of {len(actual_collaborators)} actual collaborators")