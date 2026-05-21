import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Download, Printer, TrendingUp, TrendingDown } from 'lucide-react'
import type { CreditScoreDetail } from '../types'

interface ShapReportProps {
    applicationId: number
    open: boolean
    onClose: () => void
    shapData: CreditScoreDetail | null
}

export default function ShapReport({ applicationId, open, onClose, shapData }: ShapReportProps) {
    const [loading, setLoading] = useState(false)

    const handlePrint = () => {
        window.print()
    }

    const handleDownloadPDF = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('jwt_token') || localStorage.getItem('admin_token')
            const isAdmin = !!localStorage.getItem('admin_token')
            const endpoint = isAdmin
                ? `http://localhost:8000/api/v1/admin/applications/${applicationId}/shap-report/pdf`
                : `http://localhost:8000/api/v1/applications/${applicationId}/shap-report/pdf`

            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) throw new Error('Failed to generate PDF')

            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `SHAP_Report_${applicationId}.pdf`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
        } catch (error) {
            console.error('PDF download failed:', error)
            alert('Failed to download PDF. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    if (!shapData) return null

    const positiveFeatures = shapData.shap_explanations?.filter(f => f.impact === 'positive') || []
    const negativeFeatures = shapData.shap_explanations?.filter(f => f.impact === 'negative') || []

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto print:max-w-full">
                <DialogHeader className="print:hidden">
                    <DialogTitle>SHAP Explainability Report</DialogTitle>
                    <div className="flex gap-2 mt-4">
                        <Button onClick={handlePrint} variant="outline" size="sm" className="gap-2">
                            <Printer className="w-4 h-4" />
                            Print
                        </Button>
                        <Button onClick={handleDownloadPDF} variant="outline" size="sm" className="gap-2" disabled={loading}>
                            <Download className="w-4 h-4" />
                            {loading ? 'Generating...' : 'Download PDF'}
                        </Button>
                    </div>
                </DialogHeader>

                <div className="space-y-6 print:p-8" id="shap-report-content">
                    {/* Header for Print */}
                    <div className="hidden print:block text-center mb-8">
                        <h1 className="text-3xl font-bold">SHAP Explainability Report</h1>
                        <p className="text-gray-600 mt-2">Application ID: {applicationId}</p>
                        <p className="text-gray-600">Generated: {new Date().toLocaleString()}</p>
                    </div>

                    {/* Credit Score Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Credit Score Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-3 gap-4">
                                <div className="text-center p-4 bg-primary/5 rounded-lg">
                                    <div className="text-sm text-muted-foreground">Credit Score</div>
                                    <div className="text-3xl font-bold text-primary">{Math.round(shapData.credit_score)}</div>
                                </div>
                                <div className="text-center p-4 bg-muted rounded-lg">
                                    <div className="text-sm text-muted-foreground">Risk Category</div>
                                    <div className={`text-2xl font-bold capitalize ${shapData.risk_category === 'low' ? 'text-green-600' :
                                        shapData.risk_category === 'medium' ? 'text-amber-600' :
                                            'text-red-600'
                                        }`}>{shapData.risk_category}</div>
                                </div>
                                <div className="text-center p-4 bg-muted rounded-lg">
                                    <div className="text-sm text-muted-foreground">Default Risk</div>
                                    <div className="text-2xl font-bold">{(shapData.default_probability * 100).toFixed(1)}%</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* What is SHAP? */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Understanding SHAP Values</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                SHAP (SHapley Additive exPlanations) values show how each feature in your application
                                contributed to your credit score. Positive values (green) increase your score, while
                                negative values (red) decrease it. The magnitude indicates the strength of impact.
                            </p>
                        </CardContent>
                    </Card>

                    {/* Positive Factors */}
                    {positiveFeatures.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-green-600">
                                    <TrendingUp className="w-5 h-5" />
                                    Positive Factors (Improving Your Score)
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {positiveFeatures.map((feature, idx) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                                            <div className="flex-1">
                                                <div className="font-medium text-sm">{formatFeatureName(feature.feature_name)}</div>
                                                <div className="text-xs text-muted-foreground">Value: {feature.feature_value.toFixed(2)}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-sm font-bold text-green-600">+{feature.shap_value.toFixed(3)}</div>
                                                <div className="text-xs text-muted-foreground">Impact</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Negative Factors */}
                    {negativeFeatures.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-red-600">
                                    <TrendingDown className="w-5 h-5" />
                                    Negative Factors (Reducing Your Score)
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {negativeFeatures.map((feature, idx) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                                            <div className="flex-1">
                                                <div className="font-medium text-sm">{formatFeatureName(feature.feature_name)}</div>
                                                <div className="text-xs text-muted-foreground">Value: {feature.feature_value.toFixed(2)}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-sm font-bold text-red-600">{feature.shap_value.toFixed(3)}</div>
                                                <div className="text-xs text-muted-foreground">Impact</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Recommendations */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Recommendations to Improve Your Score</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2 text-sm">
                                {negativeFeatures.slice(0, 3).map((feature, idx) => (
                                    <li key={idx} className="flex items-start gap-2">
                                        <span className="text-primary mt-1">•</span>
                                        <span>{getRecommendation(feature.feature_name)}</span>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    {/* Footer */}
                    <div className="text-center text-xs text-muted-foreground pt-4 border-t">
                        <p>This report was generated using AI/ML model version: {shapData.model_version}</p>
                        <p className="mt-1">© {new Date().getFullYear()} Saral Credit - AI-Powered Credit Scoring</p>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}

function formatFeatureName(name: string): string {
    const nameMap: Record<string, string> = {
        'age': 'Age',
        'age_squared': 'Age Factor',
        'DebtRatio': 'Debt-to-Income Ratio',
        'debt_ratio_log': 'Debt Ratio (Adjusted)',
        'MonthlyIncome': 'Monthly Income',
        'monthly_income_log': 'Income Level',
        'NumberOfOpenCreditLinesAndLoans': 'Active Credit Lines',
        'NumberOfTimes90DaysLate': 'Serious Delinquencies (90+ days)',
        'NumberRealEstateLoansOrLines': 'Real Estate Loans',
        'NumberOfTime60-89DaysPastDueNotWorse': 'Late Payments (60-89 days)',
        'NumberOfDependents': 'Number of Dependents',
        'total_late_payments': 'Total Late Payments',
        'has_real_estate': 'Real Estate Ownership'
    }
    return nameMap[name] || name
}

function getRecommendation(featureName: string): string {
    const recommendations: Record<string, string> = {
        'NumberOfTimes90DaysLate': 'Avoid late payments by setting up automatic payments or reminders',
        'DebtRatio': 'Reduce your debt-to-income ratio by paying down existing debts',
        'total_late_payments': 'Maintain consistent on-time payments to build payment history',
        'NumberOfTime60-89DaysPastDueNotWorse': 'Focus on making all payments on time going forward',
        'NumberOfOpenCreditLinesAndLoans': 'Consider consolidating loans or closing unused credit lines',
        'MonthlyIncome': 'Increase income through additional work or side gigs',
        'NumberOfDependents': 'Manage household expenses efficiently',
        'has_real_estate': 'Building savings can help with future real estate investments'
    }
    return recommendations[featureName] || 'Continue building positive credit behavior'
}
