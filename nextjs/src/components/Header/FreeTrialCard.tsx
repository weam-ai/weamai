
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function TrialCard({ daysLeft, totalDays }: { daysLeft: number, totalDays: number }) {
  return (
    <Card className="w-full max-w-xs bg-white">
      <CardContent className="p-2">
        <div className="flex flex-col gap-2">
          <Badge
            variant="secondary"
            className={`w-fit px-3 py-1 rounded-full font-medium !text-font-14 ${daysLeft < 5 ? "bg-red text-white" : "bg-violet-100 text-violet-800"}`}
          >
            Free Trial
          </Badge>

          <p className="text-base text-gray-900">
            <span className={`text-font-20 ${daysLeft < 5 ? "text-red" : "text-violet-800"}`}>{daysLeft}</span>/{totalDays} days left
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

