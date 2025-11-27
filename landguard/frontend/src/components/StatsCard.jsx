/**
 * Statistics Card Component
 */

import { Card, CardContent, Typography, Box, Avatar } from '@mui/material'
import { TrendingUp, TrendingDown } from '@mui/icons-material'

const StatsCard = ({
  title,
  value,
  icon,
  color = 'primary',
  trend,
  trendValue,
  suffix = '',
}) => {
  const isPositiveTrend = trend === 'up'
  const trendColor = isPositiveTrend ? 'success.main' : 'error.main'
  const TrendIcon = isPositiveTrend ? TrendingUp : TrendingDown

  return (
    <Card
      className="card-hover"
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${color}.light 0%, ${color}.main 100%)`,
        color: 'white',
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            mb: 2,
          }}
        >
          <Box>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, mb: 1 }}>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold">
              {value}
              {suffix && (
                <Typography component="span" variant="h6" sx={{ ml: 0.5 }}>
                  {suffix}
                </Typography>
              )}
            </Typography>
          </Box>

          <Avatar
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.3)',
              width: 48,
              height: 48,
            }}
          >
            {icon}
          </Avatar>
        </Box>

        {trend && trendValue && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              color: trendColor,
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderRadius: 1,
              px: 1,
              py: 0.5,
              width: 'fit-content',
            }}
          >
            <TrendIcon fontSize="small" />
            <Typography variant="caption" fontWeight="medium" color="inherit">
              {trendValue}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              vs last month
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default StatsCard