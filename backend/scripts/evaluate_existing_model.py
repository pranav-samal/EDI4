"""
Evaluate EXISTING deployed model (xgboost_model.pkl) without retraining.

This script:
1. Loads the EXACT same dataset used for training
2. Uses IDENTICAL preprocessing and split (same random_state=42)
3. Loads the deployed model from models/xgboost_model.pkl
4. Evaluates on the SAME test set
5. Prints comprehensive metrics
6. Saves results to evaluation_report.txt

Usage:
    python scripts/evaluate_existing_model.py --data data/cs-training.csv --model models/xgboost_model.pkl
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, 
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report, 
    confusion_matrix,
    roc_curve
)
import joblib
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def preprocess_data(df: pd.DataFrame) -> tuple:
    """
    EXACT SAME preprocessing as train_model.py
    This ensures we evaluate on the same data distribution
    """
    print("Preprocessing data (identical to training)...")
    
    # Handle missing values
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
    df['NumberOfDependents'] = df['NumberOfDependents'].fillna(0)
    
    # Remove extreme outliers
    df = df[df['DebtRatio'] <= 10]
    df = df[df['age'] >= 18]
    df = df[df['age'] <= 100]
    
    # Feature engineering
    df['age_squared'] = df['age'] ** 2
    df['debt_ratio_log'] = np.log1p(df['DebtRatio'])
    df['monthly_income_log'] = np.log1p(df['MonthlyIncome'])
    df['total_late_payments'] = (
        df['NumberOfTimes90DaysLate'] + 
        df['NumberOfTime60-89DaysPastDueNotWorse'] +
        df['NumberOfTime30-59DaysPastDueNotWorse']
    )
    df['has_real_estate'] = (df['NumberRealEstateLoansOrLines'] > 0).astype(int)
    
    # Select features (SAME ORDER as training)
    feature_cols = [
        'age', 'age_squared',
        'DebtRatio', 'debt_ratio_log',
        'MonthlyIncome', 'monthly_income_log',
        'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate',
        'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse',
        'NumberOfDependents',
        'total_late_payments',
        'has_real_estate'
    ]
    
    X = df[feature_cols]
    y = df['SeriousDlqin2yrs']
    
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    return X, y, feature_cols


def evaluate_model(model, X_test, y_test, output_file='evaluation_report.txt'):
    """
    Comprehensive evaluation of the model
    """
    print("\n" + "="*80)
    print("EVALUATING DEPLOYED MODEL")
    print("="*80)
    
    # Predictions
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    
    # Calculate all metrics
    auc = roc_auc_score(y_test, y_pred_proba)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # Additional metrics
    specificity = tn / (tn + fp)
    npv = tn / (tn + fn)
    
    # Print results
    print("\n" + "="*80)
    print("PRIMARY METRICS")
    print("="*80)
    print(f"AUC-ROC:     {auc:.4f}  {'✅ EXCEEDS' if auc >= 0.79 else '❌ BELOW'} target (0.79)")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1 Score:    {f1:.4f}")
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX")
    print("="*80)
    print(f"True Negatives:  {tn:,} (Correctly predicted Good)")
    print(f"False Positives: {fp:,} (Incorrectly predicted Default)")
    print(f"False Negatives: {fn:,} (Missed Defaults)")
    print(f"True Positives:  {tp:,} (Correctly predicted Default)")
    
    print("\n" + "="*80)
    print("ADDITIONAL METRICS")
    print("="*80)
    print(f"Specificity:             {specificity:.4f} (Ability to identify good borrowers)")
    print(f"Negative Predictive Val: {npv:.4f} (Accuracy of good predictions)")
    
    print("\n" + "="*80)
    print("CLASSIFICATION REPORT")
    print("="*80)
    print(classification_report(y_test, y_pred, target_names=['Good (0)', 'Default (1)']))
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("MODEL EVALUATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write("PRIMARY METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"AUC-ROC:     {auc:.4f}\n")
        f.write(f"Accuracy:    {accuracy:.4f}\n")
        f.write(f"Precision:   {precision:.4f}\n")
        f.write(f"Recall:      {recall:.4f}\n")
        f.write(f"F1 Score:    {f1:.4f}\n\n")
        
        f.write("CONFUSION MATRIX\n")
        f.write("-"*80 + "\n")
        f.write(f"True Negatives:  {tn:,}\n")
        f.write(f"False Positives: {fp:,}\n")
        f.write(f"False Negatives: {fn:,}\n")
        f.write(f"True Positives:  {tp:,}\n\n")
        
        f.write("ADDITIONAL METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Specificity:             {specificity:.4f}\n")
        f.write(f"Negative Predictive Val: {npv:.4f}\n\n")
        
        f.write("CLASSIFICATION REPORT\n")
        f.write("-"*80 + "\n")
        f.write(classification_report(y_test, y_pred, target_names=['Good (0)', 'Default (1)']))
    
    print(f"\n✅ Evaluation report saved to: {output_file}")
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['Predicted Good', 'Predicted Default'],
                yticklabels=['Actual Good', 'Actual Default'])
    plt.title(f'Confusion Matrix - Deployed Model\nAUC: {auc:.4f}', fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f"✅ Confusion matrix saved to: confusion_matrix.png")
    
    # Plot ROC curve
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'Model (AUC = {auc:.4f})')
    plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--', label='Random (AUC = 0.50)')
    plt.axhline(y=0.79, color='green', linestyle=':', lw=2, label='Target AUC = 0.79')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - Deployed Model', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('roc_curve.png', dpi=300, bbox_inches='tight')
    print(f"✅ ROC curve saved to: roc_curve.png")
    
    return {
        'auc': auc,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate existing deployed model')
    parser.add_argument('--data', type=str, default='data/cs-training.csv', 
                        help='Path to training data CSV (same as used for training)')
    parser.add_argument('--model', type=str, default='models/xgboost_model.pkl',
                        help='Path to deployed model')
    args = parser.parse_args()
    
    print("="*80)
    print("DEPLOYED MODEL VERIFICATION")
    print("="*80)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.data}")
    print(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    print(f"\nLoading data from {args.data}...")
    df = pd.read_csv(args.data)
    print(f"✅ Loaded {len(df):,} records")
    
    # Preprocess (IDENTICAL to training)
    X, y, feature_cols = preprocess_data(df)
    
    # Split data (IDENTICAL random_state=42 as training)
    print("\nSplitting data (random_state=42, same as training)...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.2, random_state=42, stratify=y_temp
    )
    
    print(f"✅ Training set: {len(X_train):,} samples (not used, just for info)")
    print(f"✅ Validation set: {len(X_val):,} samples (not used, just for info)")
    print(f"✅ Test set: {len(X_test):,} samples (USED FOR EVALUATION)")
    
    # Load deployed model
    print(f"\nLoading deployed model from {args.model}...")
    model = joblib.load(args.model)
    print(f"✅ Model loaded successfully")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Number of trees: {model.n_estimators}")
    print(f"   Max depth: {model.max_depth}")
    
    # Evaluate
    metrics = evaluate_model(model, X_test, y_test)
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    print(f"✅ Model AUC: {metrics['auc']:.4f}")
    print(f"✅ Meets threshold: {metrics['auc'] >= 0.79}")
    print(f"✅ Report saved: evaluation_report.txt")
    print(f"✅ Plots saved: confusion_matrix.png, roc_curve.png")
    print("\n📸 Take screenshots of these files for your presentation!")


if __name__ == "__main__":
    main()
